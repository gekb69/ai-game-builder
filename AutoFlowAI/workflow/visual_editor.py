"""
المحرر المرئي للـ Workflow
"""
import json
import time
from pathlib import Path
from typing import Dict, Any
from .viflow import Workflow
import http.server
import socketserver
import webbrowser
import threading

class VisualFlowEditor:
    def __init__(self, workflow: Workflow):
        self.workflow = workflow
        self.html_template = self._get_html_template()

    def save_html(self, filepath: str):
        content = self.html_template.replace('{{WORKFLOW_DATA}}', json.dumps(self.workflow.to_dict(), ensure_ascii=False, indent=2))
        Path(filepath).write_text(content, encoding='utf-8')

    def show(self, port: int = 8080):
        handler = http.server.SimpleHTTPRequestHandler

        def start_server():
            with socketserver.TCPServer(("", port), handler) as httpd:
                print(f"🌐 مفتوح في المتصفح: http://localhost:{port}")
                httpd.serve_forever()

        thread = threading.Thread(target=start_server, daemon=True)
        thread.start()

        time.sleep(1)
        webbrowser.open(f'http://localhost:{port}')

    def _get_html_template(self) -> str:
        return """
<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visual Workflow Editor</title>
    <style>
        body { font-family: sans-serif; margin: 0; background-color: #f0f0f0; }
        #editor { width: 100vw; height: 100vh; }
    </style>
</head>
<body>
    <div id="editor"></div>
    <script src="https://cdn.jsdelivr.net/npm/rete@1.5.0/build/rete.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/rete-vue-render-plugin@0.5.1/build/vue-render-plugin.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/rete-connection-plugin@0.9.0/build/connection-plugin.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', async () => {
            const workflowData = {{WORKFLOW_DATA}};
            const container = document.querySelector('#editor');
            const editor = new Rete.NodeEditor('demo@0.1.0', container);
            editor.use(ConnectionPlugin.default);
            editor.use(VueRenderPlugin.default);

            const numSocket = new Rete.Socket('Number value');

            class MyComponent extends Rete.Component {
                constructor(name){
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

            const components = workflowData.nodes.map(node => new MyComponent(node.name));
            components.forEach(c => editor.register(c));

            const engine = new Rete.Engine('demo@0.1.0');
            components.forEach(c => engine.register(c));

            await editor.fromJSON(workflowData);

            editor.on('process nodecreated noderemoved connectioncreated connectionremoved', async () => {
                await engine.abort();
                await engine.process(editor.toJSON());
            });

            editor.view.resize();
            editor.trigger('process');
        });
    </script>
</body>
</html>
"""
