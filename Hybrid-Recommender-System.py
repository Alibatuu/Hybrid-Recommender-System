################################
#User Based Recommendation
################################
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.expand_frame_repr', False)
#############################################################
#Görev 1
#############################################################
def create_user_movie_df():
    # Adım 1
    movie = pd.read_csv('datasets/movie_lens_dataset/movie.csv')
    rating = pd.read_csv('datasets/movie_lens_dataset/rating.csv')
    # Adım 2
    df = rating.merge(movie, how="left", on="movieId")
    comment_counts = pd.DataFrame(df["title"].value_counts())
    # Adım 3
    rare_movies = comment_counts[comment_counts["title"] <= 10000].index
    common_movies = df[~df["title"].isin(rare_movies)]
    # Adım 4
    user_movie_df = common_movies.pivot_table(index=["userId"], columns=["title"], values="rating")
    return user_movie_df

user_movie_df = create_user_movie_df()
#############################################################
#Görev 2
#############################################################
# Adım 1
random_user = int(pd.Series(user_movie_df.index).sample(1, random_state=45).values)
# Adım 2
random_user_df = user_movie_df[user_movie_df.index == random_user]
# Adım 3
movies_watched = random_user_df.columns[random_user_df.notna().any()].tolist()
#############################################################
#Görev 3
#############################################################
# Adım 1
movies_watched_df = user_movie_df[movies_watched]
# Adım 2
user_movie_count = movies_watched_df.T.notnull().sum()
user_movie_count = user_movie_count.reset_index()
user_movie_count.columns = ["userId", "movie_count"]
# Adım 3
perc = len(movies_watched) * 60 / 100
users_same_movies = user_movie_count[user_movie_count["movie_count"] > perc]["userId"].tolist()
#############################################################
#Görev 4
#############################################################
# Adım 1
final_df = pd.concat([movies_watched_df[movies_watched_df.index.isin(users_same_movies)],
                      random_user_df[movies_watched]])
# Adım 2
corr_df = final_df.T.corr().unstack().sort_values().drop_duplicates()
corr_df = pd.DataFrame(corr_df, columns=["corr"])
corr_df.index.names = ['user_id_1', 'user_id_2']
corr_df = corr_df.reset_index()
# Adım 3
top_users = corr_df[(corr_df["user_id_1"] == random_user) & (corr_df["corr"] >= 0.65)][
    ["user_id_2", "corr"]].reset_index(drop=True)
top_users = top_users.sort_values(by='corr', ascending=False)
top_users.rename(columns={"user_id_2": "userId"}, inplace=True)
# Adım 4
rating = pd.read_csv('datasets/movie_lens_dataset/rating.csv')
top_users_ratings = top_users.merge(rating[["userId", "movieId", "rating"]], how='inner')
top_users_ratings = top_users_ratings[top_users_ratings["userId"] != random_user]
#############################################################
#Görev 5
#############################################################
# Adım 1
top_users_ratings['weighted_rating'] = top_users_ratings['corr'] * top_users_ratings['rating']
# Adım 2
recommendation_df = top_users_ratings.groupby('movieId').agg({"weighted_rating": "mean"})
recommendation_df = recommendation_df.reset_index()
# Adım 3
movies_to_be_recommend = recommendation_df[recommendation_df["weighted_rating"] > 3.5].sort_values("weighted_rating", ascending=False)
# Adım 4
movie = pd.read_csv('datasets/movie_lens_dataset/movie.csv')
movies_to_be_recommend.merge(movie[["movieId", "title"]]).head()
################################
# Item Based Recommendation
################################
# Adım 1
import pandas as pd
pd.set_option('display.max_columns', 500)
movie = pd.read_csv('datasets/movie_lens_dataset/movie.csv')
rating = pd.read_csv('datasets/movie_lens_dataset/rating.csv')
# Adım 2
movieID = rating[(rating["userId"] == random_user) & (rating["rating"] == 5 )].sort_values("timestamp", ascending=False).iloc[0, 1]
movie_title = movie.loc[(movie.movieId == movieID), ["title"]].values[0].tolist()
# Adım 3
item_movie_df = user_movie_df[movie_title[0]]
# Adım 4
corr_df_item_based = user_movie_df.corrwith(item_movie_df).sort_values(ascending=False)
# Adım 5
corr_df_item_based = corr_df_item_based[corr_df_item_based.index != movie_title[0]]
corr_df_item_based=corr_df_item_based.reset_index()
item_based_recommended = corr_df_item_based["title"].tolist()

