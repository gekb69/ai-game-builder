

app = Flask(__name__)

# بيانات افتراضية للبحث
data = [
    "Python is a programming language.",
    "Flask is a web framework for Python.",
    "Machine learning is a fascinating field.",
    "Data science combines statistics and programming.",
    "Artificial intelligence is the future."
]

# قالب HTML كـ string
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام البحث</title>
</head>
<body>
    <h1>نظام البحث</h1>
    <form method="POST">
        <input type="text" name="query" placeholder="أدخل نص البحث هنا" required>
        <button type="submit">بحث</button>
    </form>
    <h2>النتائج:</h2>
    <ul>
        {% for result in results %}
            <li>{{ result }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        query = request.form.get('query')
        results = [item for item in data if query.lower() in item.lower()]
    return render_template_string(HTML_TEMPLATE, results=results)

if __name__ == '__main__':
    app.run(debug=True)
