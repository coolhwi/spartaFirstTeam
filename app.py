# 필수 라이브러리
'''
0. Flask : 웹서버를 시작할 수 있는 기능. app이라는 이름으로 플라스크를 시작한다
1. render_template : html파일을 가져와서 보여준다
'''
from flask import Flask, render_template, request,redirect,url_for,flash,jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
#DB기본 코드
import os


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'database.db')

db = SQLAlchemy(app)

# viewcount.db를 위한 데이터베이스 URI 설정
app.config['SQLALCHEMY_BINDS'] = {
    'viewcount': 'sqlite:///' + os.path.join(basedir, 'viewcount.db')
}

class ViewCount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False, unique=True)
    count = db.Column(db.Integer, default=0)

    song = db.relationship('Song', backref=db.backref('view_count_relation', uselist=False))

    def __repr__(self):
        return f'노래 ID {self.song_id}의 조회수: {self.count}'

class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(10000), nullable=False)

    def __repr__(self):
        return f'{self.username} {self.title} 추천 by {self.username}'

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    name = '김동휘'
    motto = "행복해서 웃는게 아니라 웃어서 행복합니다."

    context = {
        "name": name,
        "motto": motto,
    }
    return render_template('motto.html', data=context)

@app.route("/music/")
def music():
    song_lit = Song.query.all() # 데이터베이스에 있는 모든 음악 데이터가 song_list에 들어가게 된다.
    return render_template('music.html',data = song_lit)

@app.route("/music/<username>/")
def render_music_filter(username):
    filter_list = Song.query.filter_by(username=username).all()# 데이터베이스에 있는 모든 음악 데이터가 song_list에 들어가게 된다.
    return render_template('music.html',data = filter_list)

@app.route("/iloveyou/<name>/")
def iloveyou(name):
    motto = f"{name}야 난 너뿐이야!"

    context = {
        'name': name,
        'motto': motto,
    }
    return render_template('motto.html', data=context)

@app.route("/music/create/")
def music_create():
    # form에서 보낸 데이터 받아오기 사용자가 입력한 데이터를 받는거다.
    username_receive = request.args.get("username")
    title_receive = request.args.get("title")
    artist_receive = request.args.get("artist")
    img_url_receive = request.args.get("img_url")

    #데이터를 DB에 저장하기. 
    #첫번째 스탭은 데이터베이스를 만드는 것이다.
    song = Song(username = username_receive, title = title_receive, artist = artist_receive, image_url = img_url_receive)
    db.session.add(song)
    db.session.commit()
    return redirect(url_for('render_music_filter', username=username_receive))

@app.route("/music/delete/<int:id>",methods=['POST'])
def music_delete(id):
    song = Song.query.filter_by(id=id).first()
    if song:
        db.session.delete(song)
        db.session.commit()
        
    return redirect(url_for('music'))
    


# 노래 조회수 증가 함수
@app.route("/increase_view_count", methods=['POST','GET'])
def increase_view_count():
    song_id = request.form.get('song_id')
    song = Song.query.get(song_id)
    if song:
        view_count = ViewCount.query.filter_by(song_id=song_id).first()
        if view_count:
            view_count.count += 1
        else:
            view_count = ViewCount(song_id=song_id, count=1)
            db.session.add(view_count)
        db.session.commit()
        return jsonify({"message": "View count increased successfully"})
    else:
        return jsonify({"error": "Song not found"}), 404
# @app.route("/music/<id>")
# def music_delete_id():
#     song_lit = Song.query.all() # 데이터베이스에 있는 모든 음악 데이터가 song_list에 들어가게 된다.
#     return render_template('music.html',data = song_lit)

if __name__ == "__main__":
    app.run(debug=True)