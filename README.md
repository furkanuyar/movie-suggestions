# Movie Suggestions Twitter Bot

A Twitter bot that automatically posts curated movie suggestions and interacts with users. It fetches movie data, shares engaging tweets with **posters and trailers**, likes relevant content, and can follow/unfollow users in a user-like manner.

## Features

- **Automated Movie Posts**  
  Periodically selects and tweets movie suggestions using the TMDB (The Movie Database) API.

- **Posters & Trailers**  
  Each tweet includes a high-quality movie poster and a trailer link to engage users more effectively.

- **Auto Like Tweets**  
  Likes tweets containing specific movie-related keywords to improve visibility and engagement.

- **Follow & Unfollow Users**  
  Enables user-friendly following and unfollowing based on interest:
  - Follows users who tweet about movies (by keywords/hashtags)
  - Unfollows users who don’t follow back after some time
  - Respects Twitter rate limits and simulates human-like behavior

> **Note**: Follow/unfollow behavior is implemented responsibly to comply with Twitter's automation policies.

## Tech Stack

- **Python**
- **Twitter API v2**
- **TMDB API**
