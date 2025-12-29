from db.session import SessionLocal
from db.model import Word


def get_session():
    return SessionLocal()


def create_word(session, wordDetails):
    try:
        session.add(wordDetails)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e


def get_wordlist(session, userId):
    return (
        session.query(Word)
        .filter(Word.user_id == userId)
        .order_by(Word.updated_at.desc())
        .all()
    )


def get_word(session, wordId, userId):
    return (
        session.query(Word)
        .filter(Word.word_id == wordId, Word.user_id == userId)
        .first()
    )


def update_word(session, wordId, userId, wordDetails):
    try:
        word = (
            session.query(Word)
            .filter(Word.word_id == wordId, Word.user_id == userId)
            .first()
        )
        if word is None:
            return False
        else:
            word.word = wordDetails.word
            word.meaning = wordDetails.meaning
            word.category = wordDetails.category
            word.memo = wordDetails.memo
            session.commit()
            return True
    except Exception as e:
        session.rollback()
        raise e


def delete_word(session, wordId, userId):
    try:
        word = (
            session.query(Word)
            .filter(Word.word_id == wordId, Word.user_id == userId)
            .first()
        )
        if word is not None:
            session.delete(word)
            session.commit()
            return True
        else:
            return False
    except Exception as e:
        session.rollback()
        raise e
