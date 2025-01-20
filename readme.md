<h1 align="center">EPIC GAMES SCRAPER</h1>

I make this program to scrape the epic games weekly free game and display it on my discord server.

If you want to change the code, i recommend you to understand basic html. My code is not perfect, i just want to know when the game that i want to get is free or not.

This will scrape the Epic Games Store for info on free games name and date, the data then will be forwarded to rawg to add other additional data, such as game description, all the data will be compiled and sent to a discord server.

> [!WARNING]
> NEVER PUT SENSITIVE DATA ON A PUBLIC REPOSITORY.

> [!NOTE] Environment Variable
> - RAWG Api Token
>   - Use to get the game detail.
>   - `RAWG_API`
> - Google Application Credential
>   - Use for gcloud feature
>   - `GOOGLE_APPLICATION_CREDENTIALS`
> - Project Id
>   - Use for gcloud feature
>   - `PROJECT_ID`
> - Database Name
>   - Use for gcloud feature
>   - `DATABASE_NAME`

## GOOGLE CLOUD

The only use of the google cloud api is to store discord credential, update date, and last sent date.

This feature can be disabled by reading the [main](main.py) file.

> [!NOTE] REQUIRED GOOGLE CLOUD API
> - [Firestore](https://cloud.google.com/firestore)