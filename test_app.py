from app import app
from unittest import TestCase

from models import db, connect_db, Message, User, Follows
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///phoodie'
from app import app, CURR_USER_KEY

db.create_all()


app.config['WTF_CSRF_ENABLED'] = False


class PhoodieTest(TestCase):
    def test_signup_form(self):
       with app.test_client() as client:
           res = client.get('/')
           html = res.get_data(as_text=True)
           self.assertEqual(res.status_code, 200)
           self.assertIn('<button > Lets Go </button>', html)
    
    def test_profile_update_form(self):
        with app.test_client() as client:
            res = client.post('/messages/')
            self.assertEqual(res.status_code, 302)
            
    
    # test Model
            
    def test_user_model(self):
        new_user = User(
            email="test7@test.com",
            username="testuser7",
            password="HASHED_PASSWORD"
        )

        db.session.add(new_user)
        db.session.commit()
        
        
    def test_message_model(self):
        new_message = Message(
        text="test",
        user_id= 1
        )

        db.session.add(new_message)
        db.session.commit()
        
        
    def test_follows_model(self):
        new_follow = Follows(
        user_following_id=2,
        user_being_followed_id=1
        )

        db.session.add(new_follow)
        db.session.commit()
            
            
        
        
    