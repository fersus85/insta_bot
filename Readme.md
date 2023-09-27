# Bot for instagram by Deriabin

## This bot will allow you to automate your instagram's stuff.

## Features

- Login with login and password.
- Login with cookies.
- Like user's posts.
- Download user's image.
- Grab user's followers.
- Follow and like.
## Installing with Poetry

1. Dowload repo ```git@github.com:fersus85/insta_bot.git```
2. Go in project folder and use command ```poetry install```
## Usages
1. Open insta_bot.py and scroll tothe end of file
2. Create instance of class InstagramBot with your instagram credentials
3. Use method 'login_collect_cookie'
4. For download images from insta page use method 'download_img'
5. For collect user's posts in file  use 'collect_posts_user(save_to_file=True)'
6. For press like button on user's posts use 'likes_on_post(collect_posts_user())'
7. For grab user's followers in txt file use 'grab_followers'
8. For like user's posts and follow him use 'follow_and_like(path_to_file_you_earned_use_grab_followers)'
9. For exit use 'close_browser' method
