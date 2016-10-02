import logging

import time
import apiclient
from models import Session, Question, Answer, QuestionLog

# log config
logging.basicConfig(filename='vwyf.log',level=logging.INFO)

def add_answer(question_id, answer):
  session = Session()
  answer = Answer(
      question_id = question_id,
      answer=answer,
      created_at = time.ctime())
  session.add(answer)
  session.commit()

# log means question currently being displayed
def log_question(question_id):
  session = Session()
  log = QuestionLog(
      question_id=question_id,
      timestamp=time.ctime())
  session.add(log)
  session.commit()

def _get_questions_map(questions):
  return dict(map(lambda q: (q.id, q), questions))

def sync_local_questions(remote_questions):
  session = Session()
  local_questions = session.query(Question).all()
  local_questions_map = _get_questions_map(local_questions)
  remote_questions_map = _get_questions_map(remote_questions)

  # insert or update questions
  for q in remote_questions:
    local_question = local_questions_map.get(q.id)
    if (local_question):
      local_question.question = q.question
      local_question.option_a = q.option_a
      local_question.option_b = q.option_b
      local_question.priority = q.priority
      local_question.created_at = q.created_at
    else:
      session.add(q)

  # remove questions deleted from server
  for q in local_questions:
    if (not remote_questions_map.get(q.id)):
      session.delete(q)

  session.commit()

def save_answers_to_server(post):
  session = Session()

  # pull 30 unsaved answers from local db
  recent_unsaved_answers = session.query(Answer).\
      filter(Answer.saved_to_server == 0).\
      limit(40).\
      all()

  # post answers to server and set saved flag when post succeeded
  if (len(recent_unsaved_answers) > 0 and post(recent_unsaved_answers)):
    for ans in recent_unsaved_answers:
      ans.saved_to_server = 1

    session.commit()

def get_next_question():
  #wip
  session = Session()
