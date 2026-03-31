from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)

# Add your API key here
client = Groq(api_key="YOUR_GROQ_API_KEY_HERE")


@app.route("/")
def home():
    return render_template("index.html")


# Detect programming language (basic logic)
def detect_language(code):
    if "import java" in code or "public class" in code:
        return "Java"
    elif "#include" in code:
        return "C/C++"
    elif "def " in code:
        return "Python"
    elif "function" in code or "console.log" in code:
        return "JavaScript"
    else:
        return "Unknown"


@app.route("/explain", methods=["POST"])
def explain():
    try:
        data = request.get_json()

        code = data.get("code")
        prog_lang = data.get("language")   # programming language
        explain_lang = data.get("lang")    # explanation language

        if not code or code.strip() == "":
            return jsonify({"error": "Please enter some code."})

        # Auto detect programming language
        if prog_lang == "auto" or not prog_lang:
            prog_lang = detect_language(code)

        # Step 1: Generate explanation in English
        prompt = f"""
You are an expert programming teacher.

Explain the following {prog_lang} code in SIMPLE, beginner-friendly English.

Give:
1. Step-by-step explanation
2. What each part does
3. Keep it easy to understand

Code:
{code}
"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        explanation = completion.choices[0].message.content

        # Step 2: Translate if needed
        if explain_lang and explain_lang.lower() != "english":

            translate_prompt = f"""
Translate the following explanation into {explain_lang}.
Keep it simple and clear.

Text:
{explanation}
"""

            completion2 = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": translate_prompt}]
            )

            explanation = completion2.choices[0].message.content

        return jsonify({
            "language": prog_lang,
            "result": explanation
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": "Something went wrong. Try again."})


if __name__ == "__main__":
    app.run(debug=True)