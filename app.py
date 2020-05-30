from flask import Flask, request, render_template, redirect, session, jsonify, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

app = Flask(__name__)

app.config['SECRET_KEY'] = 'df65g4df6g46df5g4'
debug = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

@app.route('/')
def start_survey():
    """Renders choose survey page"""

    return render_template("pick_survey.html")

@app.route('/start_survey')
def pick_survey():
    """Renders home survey start page according to chosen survey"""
    
    title = request.args["pick_survey"]
    picked_survey = surveys[title]
    session["survey_title"] = title

    return render_template("start_survey.html", 
                            title=picked_survey.title, 
                            instructions=picked_survey.instructions,
                            )

@app.route('/session_init')
def start_session():
    """Initializes the session to store answer list data"""

    session["responses"] = []
    return redirect("/questions/0")

@app.route('/questions/<int:question_num>')
def show_question(question_num):
    """Show survey numbered question page"""

    responses = session["responses"]
    survey = surveys[session["survey_title"]]
    survey_title = survey.title
    length = len(survey.questions)
    if len(responses) >= length:
        return redirect("/thankyou")
    elif question_num != len(responses):
        flash("You're trying to access an invalid question")
        return redirect(f"/questions/{len(responses)}")
    else:
        survey_question = survey.questions[question_num].question
        question_choices = survey.questions[question_num].choices
        if_comments = survey.questions[question_num].allow_text
        return render_template(f"questions.html", 
                                question=survey_question,
                                title=survey_title,
                                choices=question_choices,
                                comments=if_comments
                                )
    
@app.route('/answers', methods=["POST"])
def get_answers():
    """Save answer in responses list and redirect to next question"""

    survey = surveys[session["survey_title"]]
    responses = session["responses"]
    answer = request.form["surveyAnswers"]
    comment = request.form.get("comments", default = None)
    
    if comment:
        responses.append([answer, comment])
    else:
        responses.append(answer)
    
    session["responses"] = responses

    if len(responses) == len(survey.questions):
        return redirect("/thankyou")
    else:    
        return redirect(f"/questions/{len(responses)}")        

@app.route('/thankyou')     
def show_thank_you():
    survey = surveys[session["survey_title"]]
    return render_template("/thankyou.html", title=survey.title)                

