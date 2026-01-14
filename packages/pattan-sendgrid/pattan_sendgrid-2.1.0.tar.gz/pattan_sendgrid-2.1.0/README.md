### pattan-sendgrid

pattan-sendgrid is a python package that combines the sendgrid package
with PaTTAN specific configurations.


## Quick start
1. installation
> pip install pattan-sendgrid

2. Create an environment variable 'SENDGRID_API_KEY' set its value to your sendgrid api key
>  export SENDGRID_API_KEY="YOUR SENDGRID API KEY"
3. Generate config by redirecting this output to a file or copy/paste to a file.  Keep this file out of your repo as it will contain your sendgrid api key
> pe gc 
4. Use the output from the command in step three to initialize the PattanEmail class. 


    from pattan_sendgrid import PattanEmail
     ...
    emailer = PattanEmail(PATTAN_EMAIL_CONFIG_JSON)

## Resources
1. https://docs.djangoproject.com/en/5.0/intro/reusable-apps/
2. https://pypi.org/project/sendgrid/


