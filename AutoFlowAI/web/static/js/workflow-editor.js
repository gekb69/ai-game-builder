// Rete.js Workflow Editor
document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('rete-container');
    const editor = new Rete.NodeEditor('demo@0.1.0', container);
    editor.use(ConnectionPlugin.default);
    editor.use(VueRenderPlugin.default);

    const numSocket = new Rete.Socket('Number value');

    // Define a custom component
    class MyComponent extends Rete.Component {
        constructor(name) {
            super(name);
        }
        builder(node) {
            const out1 = new Rete.Output('out1', "Output", numSocket);
            return node.addOutput(out1);
        }
        worker(node, inputs, outputs) {
            outputs['out1'] = node.data.num;
        }
    }

    const startNode = new MyComponent('Start');
    const processNode = new MyComponent('Process');
    const endNode = new MyComponent('End');

    editor.register(startNode);
    editor.register(processNode);
    editor.register(endNode);

    const engine = new Rete.Engine('demo@0.1.0');
    editor.register(engine);

    // Create nodes
    const n1 = await startNode.createNode({ num: 2 });
    const n2 = await processNode.createNode({ num: 3 });
    const n3 = await endNode.createNode({ num: 4 });

    n1.position = [80, 200];
    n2.position = [280, 200];
    n3.position = [480, 200];

    editor.addNode(n1);
    editor.addNode(n2);
    editor.addNode(n3);

    // Connect nodes
    editor.connect(n1.outputs.get('out1'), n2.inputs.get('num'));
    editor.connect(n2.outputs.get('out1'), n3.inputs.get('num'));

    editor.on('process nodecreated noderemoved connectioncreated connectionremoved', async () => {
        await engine.abort();
        await engine.process(editor.toJSON());
    });

    editor.view.resize();
    editor.trigger('process');
});
