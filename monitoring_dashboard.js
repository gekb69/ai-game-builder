/**
* 3D Neural Map Monitoring Dashboard
* Feature 86: Interactive 3D Consciousness Visualization
*/

class NeuralMap3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.nodes = new Map();
        this.connections = [];
        this.animationId = null;

        this.initialize();
    }

    initialize() {
        // Three.js setup
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0a1a);

        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 0, 50);

        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.container.appendChild(this.renderer.domElement);

        // Lighting
        const ambient = new THREE.AmbientLight(0x404040);
        this.scene.add(ambient);

        const directional = new THREE.DirectionalLight(0xffffff, 1);
        directional.position.set(50, 50, 50);
        this.scene.add(directional);

        // Controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);

        this.animate();
        this.startRealtimeUpdates();
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        this.nodes.forEach(node => node.mesh.rotation.y += 0.01);
        this.renderer.render(this.scene, this.camera);
    }

    startRealtimeUpdates() {
        const ws = new WebSocket('ws://localhost:8081/ws/monitoring');

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateNeuralMap(data);
        };
    }

    updateNeuralMap(systemData) {
        this.clearNodes();

        const { consciousness_level, awareness_score, modules } = systemData;

        // Central consciousness node
        const centralNode = this.createNode(
            {x: 0, y: 0, z: 0},
            awareness_score,
            consciousness_level,
            "consciousness"
        );
        this.nodes.set("consciousness", centralNode);

        // Module nodes
        modules?.forEach((module, index) => {
            const angle = (index / modules.length) * Math.PI * 2;
            const radius = 20;
            const position = {
                x: Math.cos(angle) * radius,
                y: Math.sin(angle) * radius,
                z: 0
            };

            const node = this.createNode(position, module.activity_level, module.name, "module");
            this.nodes.set(module.name, node);
            this.createConnection(centralNode, node, awareness_score);
        });
    }

    createNode(position, activity, label, type) {
        const geometry = new THREE.SphereGeometry(activity * 5 + 1, 32, 32);
        const material = new THREE.MeshPhongMaterial({
            color: this.getNodeColor(type, activity),
            emissive: this.getNodeColor(type, activity),
            emissiveIntensity: activity
        });

        const mesh = new THREE.Mesh(geometry, material);
        mesh.position.set(position.x, position.y, position.z);
        this.scene.add(mesh);

        return { mesh, position, activity, label, type };
    }

    getNodeColor(type, activity) {
        const colors = {
            "consciousness": 0xff6b6b,
            "module": 0x4ecdc4,
            "agent": 0x45b7d1,
            "memory": 0x96ceb4
        };
        return colors[type] || 0xffffff;
    }

    createConnection(node1, node2, strength) {
        const points = [node1.position, node2.position];
        const geometry = new THREE.BufferGeometry().setFromPoints(points);
        const material = new THREE.LineBasicMaterial({
            color: 0x888888,
            opacity: strength,
            transparent: true
        });

        const line = new THREE.Line(geometry, material);
        this.scene.add(line);
        this.connections.push(line);
    }

    clearNodes() {
        this.nodes.forEach(node => this.scene.remove(node.mesh));
        this.nodes.clear();
        this.connections.forEach(line => this.scene.remove(line));
        this.connections = [];
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.neuralMap = new NeuralMap3D('neural-map-container');
});
