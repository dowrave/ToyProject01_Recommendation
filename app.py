# 경로가 꼬여서 결국 가상환경 켰다
import pickle 
import streamlit as st 
from tmdbv3api import Movie, TMDb 

movie = Movie()
tmdb = TMDb()
tmdb.api_key = '키 입력' # 따로 텍스트 파일로 저장 : tmdb 가입 필요
tmdb.language = 'ko-KR' # 한글 포스터, 한글 제목으로 불러올 수 있음 / 없다면 원본으로 뜨는 듯?

# 영화, 코사인 유사도 불러오기 : Movie...ipynb에서 저장된 파일
movies = pickle.load(open('movies.pickle', 'rb'))
cosine_sim = pickle.load(open('cosine_sim.pickle', 'rb'))


def get_recommendations(title):
    
    # 1. 타이틀을 넣으면 인덱스를 반환
    idx = movies[movies['title'] == title].index[0] # index 자체는 arr이므로 0번째 인덱스만 뽑아 값으로 쓴다

    # 2. 코사인 매트릭스 - 내림차순 - 유사 정보 상위 10개 슬라이싱
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key = lambda x : x[1], reverse  =  True)
    sim_scores = sim_scores[1:11]

    # 3. 인덱스 정보 추출
    movie_indices = [i[0] for i in sim_scores]

    # 4. 영화 제목 얻기 - API를 이용해 영화의 이미지도 같이 출력
    images = []
    titles = []
  
    for i in movie_indices:
        # movies에는 id와 title이 있다
        id = movies['id'].iloc[i]

        # 이미지 가져오기
        # 1. https://image.tmdb.org/t/p/w500 이 모든 이미지 경로 앞에 붙는다 (w500은 이미지 크기)
        # 2. 각 데이터의 detail 에는 backdrop_path나 logo_path가 있는데, 앞에 /가 있다. 상대경로라는 뜻
        detail = movie.details(id)

        # 포스터가 없는 경우 예외처리
        image_path = detail['poster_path']
        if image_path: 
            image_path = 'https://image.tmdb.org/t/p/w500' + image_path
        else: 
            image_path = 'no_image.jpg'

        images.append(image_path)
        titles.append(detail['title']) # title 정보가 이미 있지만, tmdb는 언어 설정이 가능하다 -> 한글로 바꿀 수 있다는 뜻

    return images, titles



# 웹 구축
st.set_page_config(layout = 'wide') # wide 쓰지 않으면 좁게 나옴
st.header('MyFlix') # 제목

movie_list = movies['title'].values
title = st.selectbox('Choose a movie you like', movie_list) # 안내 문구, 이용할 리스트
if st.button('Recommend'): 
    # 프로그레스 바
    with st.spinner('plz wait...'): # spinner가 프로그레스 바 : 빙글빙글 돈다

        images, titles = get_recommendations(title)

        # 웹페이지에 표시 : 2줄에 나눠 5개씩, 총 10개의 데이터
        idx = 0
        for i in range(0, 2):
            cols = st.columns(5)
            for col in cols:
                col.image(images[idx])
                col.write(titles[idx])
                idx += 1



