// Three.js Background Animation
// Creates a 3D particle network effect with dynamic lighting and shadows

let scene, camera, renderer;
let particles, floatingShapes = [];
let mouseX = 0;
let mouseY = 0;
let windowHalfX = window.innerWidth / 2;
let windowHalfY = window.innerHeight / 2;
let pointLight;

function init() {
    const container = document.getElementById('canvas-container');
    if (!container) return;

    // SCENE
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x1a1a2e, 0.0015); // Dark blue/purple fog matching theme

    // CAMERA
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 1, 2000);
    camera.position.z = 1000;

    // RENDERER
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setClearColor(0x000000, 0); // Transparent background
    renderer.shadowMap.enabled = true; // Enable Shadows
    renderer.shadowMap.type = THREE.PCFSoftShadowMap; // Soft shadows
    renderer.domElement.style.pointerEvents = 'none';
    container.appendChild(renderer.domElement);

    // LIGHTING
    // Ambient light for base illumination
    const ambientLight = new THREE.AmbientLight(0x404040, 0.5); // Soft white light
    scene.add(ambientLight);

    // Directional light (Sun-like)
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(500, 1000, 500);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 0.5;
    dirLight.shadow.camera.far = 2000;
    scene.add(dirLight);

    // Dynamic Point Light (Will move in animate loop)
    pointLight = new THREE.PointLight(0x4ecdc4, 2, 800); // Teal light
    pointLight.position.set(0, 0, 500);
    pointLight.castShadow = true;
    scene.add(pointLight);

    // Helper to see light position (Optional, commented out)
    // const pointLightHelper = new THREE.PointLightHelper(pointLight, 10);
    // scene.add(pointLightHelper);


    // PARTICLES (Original Effect - Digital Dust)
    const kr_geometry = new THREE.BufferGeometry();
    const kr_materials = [];
    const points = [];

    // Create 800 random particles
    for (let i = 0; i < 800; i++) {
        const x = Math.random() * 2000 - 1000;
        const y = Math.random() * 2000 - 1000;
        const z = Math.random() * 2000 - 1000;
        points.push(x, y, z);
    }

    kr_geometry.setAttribute('position', new THREE.Float32BufferAttribute(points, 3));

    // Particle material
    const kr_material = new THREE.PointsMaterial({
        color: 0x4ecdc4, // Teal/Cyan color
        size: 3,
        transparent: true,
        opacity: 0.6,
        sizeAttenuation: true
    });

    particles = new THREE.Points(kr_geometry, kr_material);
    scene.add(particles);

    // FLOATING 3D SHAPES (For Shadow & Lighting Showcase)
    const geometries = [
        new THREE.OctahedronGeometry(20, 0),
        new THREE.BoxGeometry(25, 25, 25),
        new THREE.TetrahedronGeometry(20, 0)
    ];

    // Standard material reacts to light
    const shapeMaterial = new THREE.MeshStandardMaterial({
        color: 0x2c3e50, // Dark base color
        roughness: 0.4,
        metalness: 0.6,
        transparent: true,
        opacity: 0.8
    });

    // Create 30 random floating shapes
    for (let i = 0; i < 30; i++) {
        const randGeom = geometries[Math.floor(Math.random() * geometries.length)];
        const mesh = new THREE.Mesh(randGeom, shapeMaterial.clone());

        // Random Position
        mesh.position.x = Math.random() * 1600 - 800;
        mesh.position.y = Math.random() * 1000 - 500;
        mesh.position.z = Math.random() * 800 - 400;

        // Random Rotation
        mesh.rotation.x = Math.random() * 2 * Math.PI;
        mesh.rotation.y = Math.random() * 2 * Math.PI;

        // Random Scale
        const scale = Math.random() * 1 + 0.5;
        mesh.scale.set(scale, scale, scale);

        // Shadows
        mesh.castShadow = true;
        mesh.receiveShadow = true;

        scene.add(mesh);
        floatingShapes.push({
            mesh: mesh,
            rotSpeedX: (Math.random() - 0.5) * 0.02,
            rotSpeedY: (Math.random() - 0.5) * 0.02
        });
    }

    // EVENTS
    document.addEventListener('mousemove', onDocumentMouseMove, false);
    window.addEventListener('resize', onWindowResize, false);
}

function onWindowResize() {
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();

    renderer.setSize(window.innerWidth, window.innerHeight);
}

function onDocumentMouseMove(event) {
    mouseX = event.clientX - windowHalfX;
    mouseY = event.clientY - windowHalfY;
}

function animate() {
    requestAnimationFrame(animate);
    render();
}

function render() {
    const time = Date.now() * 0.0005;
    const timefast = Date.now() * 0.001;

    // Moving Camera Perception
    camera.position.x += (mouseX - camera.position.x) * 0.05;
    camera.position.y += (-mouseY - camera.position.y) * 0.05;
    camera.lookAt(scene.position);

    // Rotate Particles
    if (particles) {
        particles.rotation.y = time * 0.2;
    }

    // Animate Floating Shapes
    floatingShapes.forEach(item => {
        item.mesh.rotation.x += item.rotSpeedX;
        item.mesh.rotation.y += item.rotSpeedY;

        // Gentle Bobbing
        item.mesh.position.y += Math.sin(time + item.mesh.position.x) * 0.2;
    });

    // Animate Point Light (Lighting Transformation)
    if (pointLight) {
        pointLight.position.x = Math.sin(timefast) * 600;
        pointLight.position.y = Math.cos(timefast * 0.7) * 400;
        pointLight.position.z = Math.sin(timefast * 0.3) * 600;

        // Optional: Change light color slightly over time
        // pointLight.color.setHSL(Math.sin(time * 0.5) * 0.1 + 0.5, 0.5, 0.5);
    }

    renderer.render(scene, camera);
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    init();
    animate();
});
