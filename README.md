# fastApply

fastApply is an application that allows you to quickly apply to any job posting.  
You only need to provide the job description text and the email subject line.

The program will automatically:

- Identify the advertiser's email address.  
- Use artificial intelligence to select the most suitable résumé to send.  
- Send the email automatically using the configuration defined in your `.env` file.  
- Load résumé profiles from an external `profiles.json` file.

---

## `.env` Configuration File

You must create a file named `.env` in the root directory of the project.  
Below is an example configuration (replace the placeholders with your real values):

```bash
GMAIL_APP_PASSWORD='************'
GMAIL_USER='********@gmail.com'
AUTOEMAIL_MENSAJE="Good morning, I'm interested in the position and have attached my résumé.\n\nBest regards,\n********\nPhone: **********\n\n---\nEmail automatically generated with IA © fastApply"
PERFILES_PATH='./profiles.json'
```

**Important:**  
If you use Gmail, you’ll need to create an **App Password** in your Google Account and use it as the value of `GMAIL_APP_PASSWORD`.  
This is required because Gmail no longer allows direct login with your main password for third-party applications.

---

## `profiles.json` File

You must also create a file named `profiles.json` in the same directory as your script.  
This file defines all your résumé profiles.  
Here is an example:

```json
{
    "data science": {
        "descripcion": "Data Science Profile",
        "archivo": "/cvpath/DS.pdf"
    },
    "backend": {
        "descripcion": "Backend Profile",
        "archivo": "/cvpath/BE.pdf"
    }
}
```

## Main Features

- Automatic processing of job posting text.  
- Detection of the advertiser’s contact email.  
- Intelligent résumé selection according to job type.  
- Fully automated email sending.  
- Configurable through environment variables.  
- Easy management of multiple résumé profiles via `profiles.json`.

---

## Future Improvements

- Lightweight graphical interface.  
- Compatibility with multiple job platforms.  
- Tracking of applications and automatic replies.

---

## Author

Project developed by **Jose Duran**  
© 2025 — fastApply
