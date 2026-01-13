const DEBUG = false;

function createShader(gl, type, ...sources) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, sources.join("\n"));
  gl.compileShader(shader);
  if (gl.getShaderParameter(shader, gl.COMPILE_STATUS)) return shader;
  throw new Error(gl.getShaderInfoLog(shader));
}
function createProgram(gl, ...shaders) {
  const program = gl.createProgram();
  for (const shader of shaders) gl.attachShader(program, shader);
  gl.linkProgram(program);
  if (gl.getProgramParameter(program, gl.LINK_STATUS)) return program;
  throw new Error(gl.getProgramInfoLog(program));
}
let uniform_types = (() => {
  let core = {
    float: "uniform1fv",
    int: "uniform1iv",
    bool: "uniform1iv",
    sampler2D: "uniform1i", // Textures use integer texture units
  };

  let variations = {};
  for (const prefix of ["f", "i"]) {
    let type_prefix = prefix;
    if (prefix == "f") type_prefix = "";
    for (const v of [2, 3, 4]) {
      // set vectors
      variations[`${type_prefix}vec${v}`] = `uniform${v}${prefix}v`;
      for (const u of [2, 3, 4]) {
        let t = u == v ? `${u}` : `${u}x${v}`;
        variations[`${type_prefix}mat${t}`] = `uniformMatrix${t}${prefix}v`;
      }
    }
  }

  return Object.assign({}, variations, core );
})();

let inverted_uniform_types = (new Map(
    Object.entries(uniform_types).map(([k, v]) => [v, k])
));

function createTexture(gl, data) {
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);

  // Set texture parameters
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);

  return texture;
}

function updateTexture(gl, texture, data) {
  if (DEBUG) {
    console.log("updateTexture called with:", data);
    console.log("data type:", data?.constructor?.name);
    console.log("data is Array?", Array.isArray(data));
  }

  gl.bindTexture(gl.TEXTURE_2D, texture);

  let height, width, channels, uint8Data;

  // Handle nested array format from anywidget numpy serialization
  if (Array.isArray(data)) {
    if (DEBUG) console.log("Processing nested array format");
    height = data.length;
    width = data[0]?.length || 0;
    channels = data[0]?.[0]?.length || 0;

    console.log(`Detected dimensions: ${height}x${width}x${channels}`);

    // Flatten nested array to Uint8Array
    uint8Data = new Uint8Array(height * width * channels);
    let idx = 0;
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        for (let c = 0; c < channels; c++) {
          uint8Data[idx++] = data[y][x][c];
        }
      }
    }
  } else if (data && data.buffer instanceof ArrayBuffer) {
    // Handle DataView/TypedArray format
    if (DEBUG) console.log("Processing DataView/TypedArray format");
    const shape = data.shape || [data.height, data.width, data.channels];
    height = shape[0];
    width = shape[1];
    channels = shape[2];

    if (data instanceof Uint8Array) {
      uint8Data = data;
    } else {
      uint8Data = new Uint8Array(data.buffer);
    }
  } else {
    if (DEBUG) console.error("Unknown data format:", data);
    return;
  }

  const format = channels === 4 ? gl.RGBA : gl.RGB;
  if (DEBUG) {
    console.log(`Texture dimensions: ${width}x${height}x${channels}`);
    console.log("uint8Data length:", uint8Data.length);
    console.log("Expected length:", width * height * channels);
  }

  gl.texImage2D(
    gl.TEXTURE_2D,
    0,                // level
    format,           // internal format
    width,
    height,
    0,                // border
    format,           // format
    gl.UNSIGNED_BYTE, // type
    uint8Data
  );

  console.log("Texture uploaded to GPU");
}

// Create an empty RGBA8 texture and FBO as a render target
function createRenderTarget(gl, width, height) {
  const tex = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, tex);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.texImage2D(
    gl.TEXTURE_2D,
    0,
    gl.RGBA,
    width,
    height,
    0,
    gl.RGBA,
    gl.UNSIGNED_BYTE,
    null
  );
  const fbo = gl.createFramebuffer();
  gl.bindFramebuffer(gl.FRAMEBUFFER, fbo);
  gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
  gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  return { texture: tex, fbo };
}

function createPingPong(gl, width, height) {
  const a = createRenderTarget(gl, width, height);
  const b = createRenderTarget(gl, width, height);
  let front = a;
  let back = b;
  return {
    get front() { return front; },
    get back() { return back; },
    swap() { const tmp = front; front = back; back = tmp; },
  };
}

// Minimal present program to blit a texture to the default framebuffer
function createPresentProgram(gl) {
  const vs = createShader(
    gl,
    gl.VERTEX_SHADER,
    `#version 300 es\n` +
      `in vec4 a_position;\n` +
      `out vec2 v_uv;\n` +
      `void main(){ v_uv = (a_position.xy+1.0)*0.5; gl_Position = a_position; }`
  );
  const fs = createShader(
    gl,
    gl.FRAGMENT_SHADER,
    `#version 300 es\nprecision highp float;\n` +
      `in vec2 v_uv;\n` +
      `uniform sampler2D u_tex;\n` +
      `out vec4 fragColor;\n` +
      `void main(){ fragColor = texture(u_tex, v_uv); }`
  );
  const program = createProgram(gl, vs, fs);
  const vao = gl.createVertexArray();
  gl.bindVertexArray(vao);
  const posLoc = gl.getAttribLocation(program, "a_position");
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(
    gl.ARRAY_BUFFER,
    new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
    gl.STATIC_DRAW
  );
  gl.enableVertexAttribArray(posLoc);
  gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);
  return { program, vao };
}

// Webcam provider
async function createWebcam(gl) {
  let stream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
  } catch (e) {
    if (DEBUG) console.warn("Webcam unavailable:", e);
    return { texture: createRenderTarget(gl, 1, 1).texture, video: null, ready: false };
  }
  const video = document.createElement("video");
  video.srcObject = stream;
  video.muted = true;
  video.playsInline = true;
  await video.play();

  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  return { texture, video, ready: true };
}

// Keyboard provider: 256x1 texture where texel.x is 1.0 if keyDown
function createKeyboard(gl) {
  const width = 256, height = 1;
  const data = new Uint8Array(width * height * 4);
  const texture = gl.createTexture();
  gl.bindTexture(gl.TEXTURE_2D, texture);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, data);

  const setKey = (code, down) => {
    if (code < 0 || code >= 256) return;
    const idx = code * 4;
    data[idx] = down ? 255 : 0;
  };
  const upload = () => {
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texSubImage2D(gl.TEXTURE_2D, 0, 0, 0, width, height, gl.RGBA, gl.UNSIGNED_BYTE, data);
  };
  return { texture, setKey, upload };
}

function shader({
  width = 200,
  height = 480,
  devicePixelRatio = window.devicePixelRatio,
  preserveDrawingBuffer = false,
  visibility, // if present, only draw when resolves
  inputs = {}, // bind inputs to uniforms
  passes = [],
  attributes = {}, // initial pipeline attribute values by name
  indices = {}, // initial pipeline index buffers by name
  globals = {}, // { time, mouse, webcam, keyboard }
  uniforms = {},
}) {
  if (DEBUG) {
    console.log("Raw uniforms input:", uniforms);
    console.log("uniform_types map:", uniform_types);
  }
  uniforms = new Map(
    Object.entries(uniforms).map(([name, value]) => {
      if (DEBUG) console.log(`Processing uniform ${name} with value:`, value);
      let [_, glslType, dims] = value.match(/([^[]+)((?:\[[\s0-9]+\])*)*/);
      if (DEBUG) console.log(`  Parsed: glslType="${glslType}", dims="${dims}"`);
      // Convert GLSL type to GL function name
      const glFunc = uniform_types[glslType];
      if (DEBUG) console.log(`  Looking up glFunc for "${glslType}":`, glFunc);
      if (!glFunc) {
        if (DEBUG) {
          console.error(`Failed to find glFunc for type "${glslType}"`);
          console.error("Available types:", Object.keys(uniform_types));
        }
        throw new Error(`unknown type: ${glslType}`);
      }
      return [name, { glslType, glFunc, dims }];
    })
  );
  if (DEBUG) console.log(uniforms);
  inputs = new Map(Object.entries(inputs));
  for (const name of inputs.keys())
    if (!uniforms.has(name)) uniforms.set(name, { glslType: "float", glFunc: "uniform1fv" });

  return function (script) {
    const source = script;
    const canvas = document.createElement("canvas");

    canvas.width = width * devicePixelRatio;
    canvas.height = height * devicePixelRatio;
    const gl = canvas.getContext("webgl2", { preserveDrawingBuffer });
    canvas.style = `max-width: 100%; width: ${width}px; height: auto; touch-action: none;`;
    if (!gl) {
      throw new Error("WebGL2 not available");
    }

    // Shared full-screen quad setup
    const vertexShader = createShader(
      gl,
      gl.VERTEX_SHADER,
      `#version 300 es\n` +
        `in vec4 a_position;\n` +
        `void main(){ gl_Position = a_position; }`
    );
    const vao = gl.createVertexArray();
    gl.bindVertexArray(vao);
    const positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    gl.bufferData(
      gl.ARRAY_BUFFER,
      new Float32Array([-1, -1, 1, -1, -1, 1, -1, 1, 1, -1, 1, 1]),
      gl.STATIC_DRAW
    );
    const present = createPresentProgram(gl);

    async function render() {
      // if (visibility !== undefined) await visibility();
      frame = undefined;
      // The draw path is set below depending on passes/backbuffer
      drawFrame();
    }

    // const ondispose = Inputs.disposal(canvas);
    let disposed = false;
    // ondispose.then(() => (disposed = true));

    function setResolutionUniform(program) {
      const u_resolution = gl.getUniformLocation(program, "iResolution");
      // Shadertoy-compat: z = 1.0
      gl.uniform3f(u_resolution, canvas.width, canvas.height, 1.0);
    }

    function resize() {
      // Recompute pixel size from CSS width to keep display crisp
      const cssWidth = width; // configured width in px
      const cssHeight = height; // configured height in px
      const pxWidth = Math.floor(cssWidth * devicePixelRatio);
      const pxHeight = Math.floor(cssHeight * devicePixelRatio);
      if (canvas.width !== pxWidth || canvas.height !== pxHeight) {
        canvas.width = pxWidth;
        canvas.height = pxHeight;
        gl.viewport(0, 0, pxWidth, pxHeight);
        render(); // uniforms set per-program at draw
      }
    }

    // Initial viewport
    gl.viewport(0, 0, canvas.width, canvas.height);
    const ro = new ResizeObserver(() => resize());
    ro.observe(canvas);
    // Global resources
    let timeEnabled = !!globals.time;
    let mouseEnabled = !!globals.mouse;
    let webcamEnabled = !!globals.webcam;
    let keyboardEnabled = !!globals.keyboard;

    // Webcam
    let webcam = { texture: null, video: null, ready: false };
    (async () => {
      if (webcamEnabled) webcam = await createWebcam(gl);
    })();

    // Keyboard
    const keyboard = keyboardEnabled ? createKeyboard(gl) : null;
    if (keyboardEnabled) {
      window.addEventListener("keydown", (e) => {
        keyboard.setKey(e.keyCode || e.which || 0, true);
        keyboard.upload();
        frame || requestAnimationFrame(render);
      });
      window.addEventListener("keyup", (e) => {
        keyboard.setKey(e.keyCode || e.which || 0, false);
        keyboard.upload();
        frame || requestAnimationFrame(render);
      });
    }

    // Per-pass programs and state
    const passList = (passes && passes.length) ? passes : [{
      name: "Main",
      glsl: source,
      time: !!globals.time,
      mouse: !!globals.mouse,
      webcam: !!globals.webcam,
      keyboard: !!globals.keyboard,
      backbuffer: !!globals.backbuffer,
    }];

    const compiled = [];
    let textureUnitCounter = 0;

    function allocTextureUnit() { return textureUnitCounter++; }

    function buildFragment(glsl, decl, outName) {
      const prolog = `#version 300 es\nprecision highp float;\nprecision highp int;\n\n${decl}\n`;
      const body = glsl.includes("void mainImage(")
        ? glsl
        : `#line 1\nvoid mainImage(out vec4 fragColor, in vec2 fragCoord) {\n${glsl}\n}`;
      const epilog = `\n#line 1\nout vec4 ${outName};\nvoid main(){ mainImage(${outName}, gl_FragCoord.xy); }`;
      return createShader(gl, gl.FRAGMENT_SHADER, prolog + body + epilog);
    }

    // Pipeline helpers
    function buildVertexForPipeline(vertGLSL, decl, attributes, varyings) {
      const attrDecl = (attributes || []).map(a => `in ${a.type} ${a.name};`).join("\n");
      const varyDecl = (varyings || []).map(v => v.name === 'gl_Position' ? '' : `out ${v.type} ${v.name};`).join("\n");
      const prolog = `#version 300 es\nprecision highp float;\nprecision highp int;\n${attrDecl}\n${varyDecl}\n${decl}\n`;

      function extractMainBody(src) {
        const mainIdx = src.indexOf("void main");
        if (mainIdx >= 0) {
          const braceStart = src.indexOf("{", mainIdx);
          if (braceStart >= 0) {
            let depth = 0;
            for (let i = braceStart; i < src.length; i++) {
              const ch = src[i];
              if (ch === '{') depth++;
              else if (ch === '}') {
                depth--;
                if (depth === 0) return src.slice(braceStart + 1, i);
              }
            }
          }
        }
        return src; // treat as body if no main
      }

      if (Array.isArray(vertGLSL)) {
        const stages = vertGLSL.map((src, i) => `void __stage${i}(){\n${extractMainBody(src)}\n}`);
        const calls = vertGLSL.map((_, i) => `__stage${i}();`).join("\n");
        const main = `void main(){\n${calls}\n}`;
        return createShader(gl, gl.VERTEX_SHADER, prolog + stages.join("\n\n") + "\n" + main);
      } else {
        const body = vertGLSL.includes("void main(") ? vertGLSL : `#line 1\nvoid main(){\n${vertGLSL}\n}`;
        return createShader(gl, gl.VERTEX_SHADER, prolog + body);
      }
    }
    function buildFragmentForPipeline(fragGLSL, decl, varyings, colorOuts) {
      const varyDecl = (varyings || []).map(v => v.name === 'gl_Position' ? '' : `in ${v.type} ${v.name};`).join("\n");
      const outDecl = (colorOuts || []).map(c => `layout(location=${c.loc||0}) out ${c.type} ${c.name};`).join("\n");
      const prolog = `#version 300 es\nprecision highp float;\nprecision highp int;\n${varyDecl}\n${decl}\n${outDecl}\n`;
      const body = fragGLSL.includes("void main(") ? fragGLSL : `#line 1\nvoid main(){\n${fragGLSL}\n}`;
      return createShader(gl, gl.FRAGMENT_SHADER, prolog + body);
    }

    // Build all passes
    for (let i = 0; i < passList.length; i++) {
      const p = passList[i];
      // Shared declarations (uniforms + built-ins)
      let decl = Array.from(
        uniforms,
        ([name, { glslType, dims }]) => `uniform ${glslType} ${name}${dims || ""};`
      ).join("\n");
      decl += `\nuniform vec3 iResolution;`;
      decl += `\nuniform vec4 iDate;`;
      if (p.time) decl += `\nuniform float iTime;\nuniform int iFrame;\nuniform float iTimeDelta;\nuniform float iFrameRate;`;
      if (p.mouse) decl += `\nuniform vec4 iMouse;`;
      if (p.webcam) decl += `\nuniform sampler2D iWebcam;`;
      if (p.keyboard) decl += `\nuniform sampler2D iKeyboard;`;
      if (p.backbuffer) decl += `\nuniform sampler2D iBackbuffer;`;
      const pInputs = Array.isArray(p.inputs) ? p.inputs : [];
      for (const inp of pInputs) {
        const t = inp.type || "sampler2D";
        decl += `\nuniform ${t} ${inp.name};`;
      }
      if (i > 0 && p.glsl) decl += `\nuniform sampler2D iPrevPass;`;

      if (p.vert && p.frag) {
        // Vertex+fragment pipeline pass
        const varyings = Array.isArray(p.varyings) ? p.varyings : [];
        const attrSpecs = Array.isArray(p.attributes) ? p.attributes : [];
        const colors = Array.isArray(p.colors) ? p.colors : [{ name: 'color0', type: 'vec4', loc: 0 }];
        const vs = buildVertexForPipeline(p.vert, decl, attrSpecs, varyings);
        const fs = buildFragmentForPipeline(p.frag, decl, varyings, colors);
        const prog = createProgram(gl, vs, fs);
        const vaoLocal = gl.createVertexArray();
        gl.bindVertexArray(vaoLocal);

        const loc = {
          iResolution: gl.getUniformLocation(prog, "iResolution"),
          iDate: gl.getUniformLocation(prog, "iDate"),
          iTime: p.time ? gl.getUniformLocation(prog, "iTime") : null,
          iFrame: p.time ? gl.getUniformLocation(prog, "iFrame") : null,
          iTimeDelta: p.time ? gl.getUniformLocation(prog, "iTimeDelta") : null,
          iFrameRate: p.time ? gl.getUniformLocation(prog, "iFrameRate") : null,
          iMouse: p.mouse ? gl.getUniformLocation(prog, "iMouse") : null,
          iWebcam: p.webcam ? gl.getUniformLocation(prog, "iWebcam") : null,
          iKeyboard: p.keyboard ? gl.getUniformLocation(prog, "iKeyboard") : null,
        };

        // Global uniforms
        const uLocs = new Map();
        const textures = new Map();
        for (const [name, u] of uniforms) {
          const l = gl.getUniformLocation(prog, name);
          uLocs.set(name, { ...u, location: l });
          if (u.glslType === "sampler2D") {
            const unit = allocTextureUnit();
            textures.set(name, { unit, texture: createTexture(gl) });
          }
        }

        // Bind attributes by name and upload initial data
        const attribs = new Map();
        let count = 0;
        for (const a of attrSpecs) {
          const locAttrib = gl.getAttribLocation(prog, a.name);
          if (locAttrib < 0) continue;
          const buffer = gl.createBuffer();
          attribs.set(a.name, { location: locAttrib, buffer, size: a.size });
          const val = attributes ? attributes[a.name] : null;
          if (val) {
            gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
            const arr = Array.isArray(val) ? new Float32Array(val.flat(2)) : (val.buffer ? new Float32Array(val.buffer) : new Float32Array(val));
            gl.bufferData(gl.ARRAY_BUFFER, arr, gl.STATIC_DRAW);
            gl.enableVertexAttribArray(locAttrib);
            gl.vertexAttribPointer(locAttrib, a.size, gl.FLOAT, false, 0, 0);
            if (!count) count = Math.floor(arr.length / a.size);
          }
        }
        if (!count) count = 3; // default fullscreen triangle when no attributes
        // Optional index buffer
        let ebo = null; let indexCount = 0; let indexType = gl.UNSIGNED_INT;
        if (p.index) {
          const name = p.index;
          const val = indices ? indices[name] : null;
          if (val) {
            ebo = gl.createBuffer();
            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, ebo);
            let arr;
            if (val instanceof Uint32Array) arr = val;
            else if (val instanceof Uint16Array) { arr = val; indexType = gl.UNSIGNED_SHORT; }
            else if (Array.isArray(val)) {
              arr = new Uint32Array(val.flat(1));
              indexType = gl.UNSIGNED_INT;
            } else if (val && val.buffer instanceof ArrayBuffer) {
              arr = new Uint32Array(val.buffer);
            }
            if (arr) {
              gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, arr, gl.STATIC_DRAW);
              indexCount = arr.length;
            }
          }
        }

        const primitive = (p.primitive || 'points');
        // Enable depth testing for 3D pipeline draws
        gl.enable(gl.DEPTH_TEST);
        // Locations for typed pipeline inputs
        const inputLocs = new Map();
        const pInputs = Array.isArray(p.inputs) ? p.inputs : [];
        for (const inp of pInputs) {
          inputLocs.set(inp.name, gl.getUniformLocation(prog, inp.name));
        }

        // Offscreen target for chaining
        const needsOffscreen = (i < passList.length - 1);
        const rt = needsOffscreen ? createRenderTarget(gl, canvas.width, canvas.height) : null;

        compiled.push({ prog, loc, uLocs, textures, spec: p, vao: vaoLocal, attribs, count, primitive, type: 'pipeline', ebo, indexCount, indexType, inputLocs, rt });
      } else {
        // Image-style pass (fragment-only)
        const fs = buildFragment(p.glsl, decl, p.out || "fragColor");
        const prog = createProgram(gl, vertexShader, fs);
        const posLoc = gl.getAttribLocation(prog, "a_position");
        gl.bindVertexArray(vao);
        gl.enableVertexAttribArray(posLoc);
        gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

        const loc = {
          iResolution: gl.getUniformLocation(prog, "iResolution"),
          iDate: gl.getUniformLocation(prog, "iDate"),
          iTime: p.time ? gl.getUniformLocation(prog, "iTime") : null,
          iFrame: p.time ? gl.getUniformLocation(prog, "iFrame") : null,
          iTimeDelta: p.time ? gl.getUniformLocation(prog, "iTimeDelta") : null,
          iFrameRate: p.time ? gl.getUniformLocation(prog, "iFrameRate") : null,
          iMouse: p.mouse ? gl.getUniformLocation(prog, "iMouse") : null,
          iWebcam: p.webcam ? gl.getUniformLocation(prog, "iWebcam") : null,
          iKeyboard: p.keyboard ? gl.getUniformLocation(prog, "iKeyboard") : null,
          iBackbuffer: p.backbuffer ? gl.getUniformLocation(prog, "iBackbuffer") : null,
          iPrevPass: i > 0 ? gl.getUniformLocation(prog, "iPrevPass") : null,
        };

        const inputLocs = new Map();
        for (const inp of pInputs) {
          inputLocs.set(inp.name, gl.getUniformLocation(prog, inp.name));
        }

        const uLocs = new Map();
        const textures = new Map();
        for (const [name, u] of uniforms) {
          const l = gl.getUniformLocation(prog, name);
          uLocs.set(name, { ...u, location: l });
          if (u.glslType === "sampler2D") {
            const unit = allocTextureUnit();
            textures.set(name, { unit, texture: createTexture(gl) });
          }
        }

        const needsOffscreen = (i < passList.length - 1) || p.backbuffer;
        const rt = needsOffscreen ? createRenderTarget(gl, canvas.width, canvas.height) : null;
        const pingpong = p.backbuffer ? createPingPong(gl, canvas.width, canvas.height) : null;
        compiled.push({ prog, loc, uLocs, textures, rt, pingpong, spec: p, inputLocs, type: 'image' });
      }
    }

    // Mouse handling (Shadertoy semantics)
    let mouseXY = [0, 0];
    let leftDown = 0;
    let rightDown = 0;
    canvas.addEventListener("contextmenu", (e) => e.preventDefault());
    canvas.addEventListener("pointerdown", (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) * devicePixelRatio;
      const y = rect.height * devicePixelRatio - (e.clientY - rect.top) * devicePixelRatio;
      e.preventDefault();
      try { canvas.setPointerCapture(e.pointerId); } catch {}
      mouseXY[0] = x; mouseXY[1] = y;
      if (e.button === 0) leftDown = 1;
      if (e.button === 2) rightDown = 1;
      frame || requestAnimationFrame(render);
    });
    canvas.addEventListener("pointerup", (e) => {
      e.preventDefault();
      if (e.button === 0) leftDown = 0;
      if (e.button === 2) rightDown = 0;
      frame || requestAnimationFrame(render);
    });
    canvas.addEventListener("pointermove", (e) => {
      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) * devicePixelRatio;
      const y = rect.height * devicePixelRatio - (e.clientY - rect.top) * devicePixelRatio;
      mouseXY[0] = x; mouseXY[1] = y;
      frame || requestAnimationFrame(render);
    });

    // Apply initial Python-provided uniforms
    function applyInitialUniforms() {
      for (const c of compiled) {
        gl.useProgram(c.prog);
        // iResolution per program
        gl.uniform3f(c.loc.iResolution, canvas.width, canvas.height, 1.0);

        // Bind user textures
        for (const [name, u] of c.uLocs) {
          const val = inputs.get(name);
          if (!val) continue;
          if (u.glslType === "sampler2D") {
            const tex = c.textures.get(name);
            updateTexture(gl, tex.texture, val);
            gl.activeTexture(gl.TEXTURE0 + tex.unit);
            gl.bindTexture(gl.TEXTURE_2D, tex.texture);
            gl.uniform1i(u.location, tex.unit);
          } else {
            const isMatrix = u.glFunc.startsWith("uniformMatrix");
            const data = [val].flat(4);
            if (isMatrix) gl[u.glFunc](u.location, false, data);
            else gl[u.glFunc](u.location, data);
          }
        }
      }
    }
    applyInitialUniforms();

    // Time tracking
    let lastTime = performance.now() * 0.001;
    let frameCount = 0;
    let frame;
    const animate = passList.some(p => p.time || p.webcam || p.backbuffer);
    function drawFrame() {
      const now = performance.now() * 0.001;
      const dt = Math.max(1e-6, now - lastTime);
      const fps = 1.0 / dt;
      lastTime = now;
      frameCount++;

      let prevTex = null;
      const hasPipeline = compiled.some(c => c.type === 'pipeline');
      if (hasPipeline) {
        gl.clearDepth(1.0);
        gl.clear(gl.DEPTH_BUFFER_BIT);
      }
      // Execute passes
      for (let i = 0; i < compiled.length; i++) {
        const c = compiled[i];
        gl.useProgram(c.prog);

        // Built-ins
        gl.uniform3f(c.loc.iResolution, canvas.width, canvas.height, 1.0);
        // iDate: year, month(1-12), day, seconds of day
        if (c.loc.iDate) {
          const d = new Date();
          const secOfDay = d.getHours() * 3600 + d.getMinutes() * 60 + d.getSeconds() + d.getMilliseconds() / 1000;
          gl.uniform4f(c.loc.iDate, d.getFullYear(), d.getMonth() + 1, d.getDate(), secOfDay);
        }
        if (c.loc.iTime) gl.uniform1f(c.loc.iTime, now);
        if (c.loc.iFrame) gl.uniform1i(c.loc.iFrame, frameCount);
        if (c.loc.iTimeDelta) gl.uniform1f(c.loc.iTimeDelta, dt);
        if (c.loc.iFrameRate) gl.uniform1f(c.loc.iFrameRate, fps);
        if (c.loc.iMouse) gl.uniform4f(c.loc.iMouse, mouseXY[0], mouseXY[1], leftDown, rightDown);

        // Webcam update
        let texUnit = textureUnitCounter + i; // not perfect, but reserve space
        if (c.loc.iWebcam && webcam.ready) {
          gl.activeTexture(gl.TEXTURE0 + texUnit);
          gl.bindTexture(gl.TEXTURE_2D, webcam.texture);
          try {
            gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
            gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, webcam.video);
            gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
          } catch {}
          gl.uniform1i(c.loc.iWebcam, texUnit);
          texUnit++;
        }

        // Keyboard texture
        if (c.loc.iKeyboard && keyboard) {
          gl.activeTexture(gl.TEXTURE0 + texUnit);
          gl.bindTexture(gl.TEXTURE_2D, keyboard.texture);
          gl.uniform1i(c.loc.iKeyboard, texUnit);
          texUnit++;
        }

        // Chain previous pass output (implicit, image-only)
        if (c.type === 'image' && c.loc.iPrevPass && prevTex) {
          gl.activeTexture(gl.TEXTURE0 + texUnit);
          gl.bindTexture(gl.TEXTURE_2D, prevTex);
          gl.uniform1i(c.loc.iPrevPass, texUnit);
          texUnit++;
        }

        if (c.type === 'image') {
          // Typed input connectors
          const pInputs = Array.isArray(c.spec.inputs) ? c.spec.inputs : [];
          for (const inp of pInputs) {
            const src = compiled[inp.from];
            const srcTex = src.spec.backbuffer ? src.pingpong.back.texture : src.rt.texture;
            const u = c.inputLocs.get(inp.name);
            if (!u) continue;
            gl.activeTexture(gl.TEXTURE0 + texUnit);
            gl.bindTexture(gl.TEXTURE_2D, srcTex);
            gl.uniform1i(u, texUnit);
            texUnit++;
          }
        } else {
          // Pipeline typed input connectors
          const pInputs = Array.isArray(c.spec.inputs) ? c.spec.inputs : [];
          for (const inp of pInputs) {
            const src = compiled[inp.from];
            const srcTex = (src.type === 'image')
              ? (src.spec.backbuffer ? src.pingpong.back.texture : src.rt.texture)
              : (src.rt ? src.rt.texture : null);
            const u = c.inputLocs && c.inputLocs.get(inp.name);
            if (!u || !srcTex) continue;
            gl.activeTexture(gl.TEXTURE0 + texUnit);
            gl.bindTexture(gl.TEXTURE_2D, srcTex);
            gl.uniform1i(u, texUnit);
            texUnit++;
          }
        }

        // Backbuffer
        if (c.spec.backbuffer && c.pingpong) {
          gl.activeTexture(gl.TEXTURE0 + texUnit);
          gl.bindTexture(gl.TEXTURE_2D, c.pingpong.back.texture);
          if (c.loc.iBackbuffer) gl.uniform1i(c.loc.iBackbuffer, texUnit);
          texUnit++;
        }

        // Where to render
        if (c.type === 'image') {
          const offscreen = (i < compiled.length - 1) || c.spec.backbuffer;
          if (offscreen) {
            const target = c.spec.backbuffer ? c.pingpong.front : c.rt;
            gl.bindFramebuffer(gl.FRAMEBUFFER, target.fbo);
            gl.viewport(0, 0, canvas.width, canvas.height);
            // Clear offscreen target to opaque black to avoid artifacts
            gl.disable(gl.DEPTH_TEST);
            gl.clearColor(0.0, 0.0, 0.0, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);
            gl.drawArrays(gl.TRIANGLES, 0, 6);
            gl.bindFramebuffer(gl.FRAMEBUFFER, null);
            // For next pass
            prevTex = (c.spec.backbuffer ? c.pingpong.front.texture : c.rt.texture);
            // swap pingpong if used
            if (c.spec.backbuffer) c.pingpong.swap();
          } else {
            // Final pass draws directly to screen
            gl.bindFramebuffer(gl.FRAMEBUFFER, null);
            gl.viewport(0, 0, canvas.width, canvas.height);
            gl.drawArrays(gl.TRIANGLES, 0, 6);
          }
        } else {
          // Pipeline draw
          const needsOffscreen = (i < compiled.length - 1);
          if (needsOffscreen && c.rt) {
            gl.bindFramebuffer(gl.FRAMEBUFFER, c.rt.fbo);
            gl.viewport(0, 0, canvas.width, canvas.height);
            // Clear offscreen target to opaque black to avoid artifacts
            gl.disable(gl.DEPTH_TEST);
            gl.clearColor(0.0, 0.0, 0.0, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);
          } else {
            gl.bindFramebuffer(gl.FRAMEBUFFER, null);
          }
          gl.bindVertexArray(c.vao);
          gl.viewport(0, 0, canvas.width, canvas.height);
          const mode = c.primitive === 'triangles' ? gl.TRIANGLES : (c.primitive === 'lines' ? gl.LINES : gl.POINTS);
          if (c.ebo && c.indexCount) {
            gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, c.ebo);
            gl.drawElements(mode, c.indexCount, c.indexType, 0);
          } else if (!c.spec.index) {
            // Non-indexed pass: draw arrays
            gl.drawArrays(mode, 0, c.count);
          } else {
            // Indexed pass with empty index buffer: skip draw to avoid spurious lines
          }
        }
      }

      // If last pass was offscreen (because of backbuffer or chaining), blit to screen
      const last = compiled[compiled.length - 1];
      if (last) {
        if (last.type === 'image') {
          const needsPresent = !!last.rt || last.spec.backbuffer;
          if (needsPresent) {
            const tex = last.spec.backbuffer ? last.pingpong.back.texture : last.rt.texture;
            gl.useProgram(present.program);
            gl.bindVertexArray(present.vao);
            const loc = gl.getUniformLocation(present.program, "u_tex");
            gl.activeTexture(gl.TEXTURE0);
            gl.bindTexture(gl.TEXTURE_2D, tex);
            gl.uniform1i(loc, 0);
            gl.drawArrays(gl.TRIANGLES, 0, 6);
          }
        } else if (last.type === 'pipeline' && last.rt) {
          // Blit final pipeline RT to screen if offscreen drawn
          const tex = last.rt.texture;
          gl.useProgram(present.program);
          gl.bindVertexArray(present.vao);
          const loc = gl.getUniformLocation(present.program, "u_tex");
          gl.activeTexture(gl.TEXTURE0);
          gl.bindTexture(gl.TEXTURE_2D, tex);
          gl.uniform1i(loc, 0);
          gl.drawArrays(gl.TRIANGLES, 0, 6);
        }
      }

      // schedule next frame if animated
      frame = animate ? requestAnimationFrame(render) : undefined;
    }

    Object.assign(canvas, {
      update(values = {}) {
        if (disposed) return false;
        // Update Python-provided uniforms
        for (const name in values) {
          for (const c of compiled) {
            const u = c.uLocs.get(name);
            if (!u) continue;
            gl.useProgram(c.prog);
            if (u.glslType === "sampler2D") {
              const tex = c.textures.get(name);
              updateTexture(gl, tex.texture, values[name]);
              gl.activeTexture(gl.TEXTURE0 + tex.unit);
              gl.bindTexture(gl.TEXTURE_2D, tex.texture);
              gl.uniform1i(u.location, tex.unit);
            } else {
              const isMatrix = u.glFunc.startsWith("uniformMatrix");
              const data = [values[name]].flat(4);
              if (isMatrix) gl[u.glFunc](u.location, false, data);
              else gl[u.glFunc](u.location, data);
            }
          }
        }
        frame || requestAnimationFrame(render);
        return true;
      },
      destroy() {
        if (disposed) return true;
        // Stop animation
        if (frame) cancelAnimationFrame(frame);
        frame = undefined;
        // Remove input listeners
        try {
          canvas.removeEventListener("contextmenu", (e) => e.preventDefault());
        } catch {}
        // Delete GL resources
        try {
          gl.useProgram(null);
          if (present && present.program) gl.deleteProgram(present.program);
          if (present && present.vao) gl.deleteVertexArray(present.vao);
          for (const c of compiled) {
            try { if (c.prog) gl.deleteProgram(c.prog); } catch {}
            if (c.type === 'image') {
              try { if (c.rt) { gl.deleteFramebuffer(c.rt.fbo); gl.deleteTexture(c.rt.texture); } } catch {}
              try { if (c.pingpong) { gl.deleteFramebuffer(c.pingpong.front.fbo); gl.deleteTexture(c.pingpong.front.texture); gl.deleteFramebuffer(c.pingpong.back.fbo); gl.deleteTexture(c.pingpong.back.texture); } } catch {}
            } else if (c.type === 'pipeline') {
              try { if (c.rt) { gl.deleteFramebuffer(c.rt.fbo); gl.deleteTexture(c.rt.texture); } } catch {}
              try { if (c.ebo) gl.deleteBuffer(c.ebo); } catch {}
              try { if (c.vao) gl.deleteVertexArray(c.vao); } catch {}
              try { if (c.attribs) { for (const m of c.attribs.values()) gl.deleteBuffer(m.buffer); } } catch {}
            }
            try { if (c.textures) { for (const info of c.textures.values()) gl.deleteTexture(info.texture); } } catch {}
          }
        } catch {}
        disposed = true;
        try { if (canvas.parentElement) canvas.parentElement.innerHTML = ""; } catch {}
        return true;
      },
    });

    // Kick off
    frame = requestAnimationFrame(render);
    return canvas;
  };
}

function render({ model, el }) {
  let uniforms = model.get("_uniforms") || {};
  let inputs = {};
  for (const name in uniforms) inputs[name] = model.get(name);

  function showErrorOverlay(msg) {
    const pre = document.createElement("pre");
    pre.textContent = String(msg);
    pre.style.cssText = "white-space: pre-wrap; color: #f55; background: #220; padding: 8px; font-size: 12px; overflow:auto; max-height: 300px;";
    el.innerHTML = "";
    el.appendChild(pre);
  }

  let canvas;
  try {
    const passes = model.get("_passes") || [];
    // Collect initial attribute and index values for pipeline passes
    const attrValues = {};
    const indexValues = {};
    for (const p of passes) {
      if (p.vert && Array.isArray(p.attributes)) {
        for (const a of p.attributes) {
          const n = a.name;
          if (attrValues[n] === undefined) attrValues[n] = model.get(n);
        }
      }
      if (p.index) {
        const n = p.index;
        if (indexValues[n] === undefined) indexValues[n] = model.get(n);
      }
    }
    const globals = {
      time: model.get("_time"),
      mouse: model.get("_mouse"),
      webcam: model.get("_webcam"),
      keyboard: model.get("_keyboard"),
      backbuffer: model.get("_backbuffer"),
    };
    canvas = shader({
      width: model.get("_width"),
      height: model.get("_height"),
      devicePixelRatio: window.devicePixelRatio,
      preserveDrawingBuffer: false,
      visibility: true,
      inputs: inputs,
      passes: passes,
      attributes: attrValues,
      indices: indexValues,
      globals,
      uniforms: uniforms,
    })(passes.length ? "" : model.get("glsl"));
  } catch (e) {
    showErrorOverlay(e?.message || e);
    return;
  }

  el.appendChild(canvas);

  // Listen for traitlet changes and update the canvas uniforms live.
  for (const name in uniforms) {
    model.on(`change:${name}`, () => {
      try {
        const val = model.get(name);
        canvas.update({ [name]: val });
      } catch (e) {
        if (DEBUG) console.error(`Failed to update uniform ${name}:`, e);
      }
    });
  }
  // Disposal from Python
  model.on('change:_destroy', () => {
    try { if (canvas.destroy) canvas.destroy(); } catch {}
  });

  // Attribute changes (pipeline): re-upload buffers and redraw
  const passes = model.get("_passes") || [];
  const attrNames = new Set();
  const indexNames = new Set();
  for (const p of passes) {
    if (p.vert && Array.isArray(p.attributes)) {
      for (const a of p.attributes) attrNames.add(a.name);
    }
    if (p.index) indexNames.add(p.index);
  }
  for (const name of attrNames) {
    model.on(`change:${name}`, () => {
      try {
        const val = model.get(name);
        for (const c of compiled) {
          if (c.type !== 'pipeline') continue;
          const meta = c.attribs && c.attribs.get(name);
          if (!meta) continue;
          gl.useProgram(c.prog);
          gl.bindVertexArray(c.vao);
          gl.bindBuffer(gl.ARRAY_BUFFER, meta.buffer);
          const arr = Array.isArray(val) ? new Float32Array(val.flat(2)) : (val.buffer ? new Float32Array(val.buffer) : new Float32Array(val));
          gl.bufferData(gl.ARRAY_BUFFER, arr, gl.STATIC_DRAW);
          gl.enableVertexAttribArray(meta.location);
          gl.vertexAttribPointer(meta.location, meta.size, gl.FLOAT, false, 0, 0);
          c.count = Math.floor(arr.length / meta.size);
        }
        // trigger redraw
        const canvasEl = el.querySelector('canvas');
        if (canvasEl && canvasEl.update) canvasEl.update({});
      } catch (e) {
        if (DEBUG) console.error(`Failed to update attribute ${name}:`, e);
      }
    });
  }
  for (const name of indexNames) {
    model.on(`change:${name}`, () => {
      try {
        const val = model.get(name);
        for (const c of compiled) {
          if (c.type !== 'pipeline') continue;
          if (!c.ebo) continue;
          gl.bindVertexArray(c.vao);
          gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, c.ebo);
          let arr;
          if (val instanceof Uint32Array) arr = val;
          else if (val instanceof Uint16Array) arr = val;
          else if (Array.isArray(val)) arr = new Uint32Array(val.flat(1));
          else if (val && val.buffer instanceof ArrayBuffer) arr = new Uint32Array(val.buffer);
          if (arr) {
            gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, arr, gl.STATIC_DRAW);
            c.indexCount = arr.length;
          }
        }
        const canvasEl = el.querySelector('canvas');
        if (canvasEl && canvasEl.update) canvasEl.update({});
      } catch (e) {
        if (DEBUG) console.error(`Failed to update index ${name}:`, e);
      }
    });
  }
}
export default { render };
