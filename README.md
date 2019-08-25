# invoicer
Python web app for keeping track of invoices

# Configuration
Create a file named `application.cfg` in your instance folder (which is a
Python file).

Set the following parameters:
*   `SECRET_KEY`: You should always create your own secret key
*   `SESSION_TIMEOUT_MINUTES`: The number of minutes before you are
    automatically logged out.  Set this to `None` or `0` to stay logged in.
*   `WKHTMLTOPDF`: The path to the `wkhtmltopdf` binary used for converting the
    HTML invoice to a PDF.
*   `NAME` (optional): Your full name.  This is used as the `<title>` for the
    generated HTML invoice.

Override any other configuration parameters as you see fit.

# PDF Generation
PDFs are generated using [wkhtmltopdf](https://wkhtmltopdf.org/).  You'll need
to install that application and set the `WKHTMLTOPDF` configuration parameter
to its path.

# Initialization
To initialize the application, follow these steps:
*   Create a virtual env for this project and activate it:  
    `conda create -n invoicer python=2`  
    `source activate invoicer`
*   Copy/clone the repository
*   Install the package  
    dev environment: `pip install -e .[test,manage]`  
    run environment: `pip install -e .[memcached]`
*   Create the instance folder and `instance/application.cfg`  
    `mkdir instance && touch instance/application.cfg`
*   Create an `env.sh` file:  
    `echo export FLASK_APP=invoicer > instance/env.sh && chmod +x instance/env.sh && . instance/env.sh`
*   Create the log folder:  
    `sudo mkdir -p /var/log/invoicer && sudo chown $USER:nginx /var/log/invoicer`
*   Run `flask initdb` (you may want to skip adding sample data)
*   Run `flask add-user` to create the first user
*   Run the application: `flask run`
*   Open the browser
*   Edit your profile: `http://127.0.0.1:5000/profile/update`
*   Create your *billable units*: `http://127.0.0.1:5000/units`
*   Add a customer: `http://127.0.0.1:5000/customers`
*   Add a new invoice: `http://127.0.0.1:5000/invoice/new`
*   Add new items to the invoice: `http://127.0.0.1:5000/invoice/1/items/new`

# Invoice Submission
Once you have added all of the items, you can click the `Submit Invoice` button.
This is available if you have set up your email server, and the customer has
an email address.

You can only submit the invoice once.  This is to prevent multiple emails to
your customer.  If you need to submit it again, download the PDF and send it
yourself.

The default is to CC `app.config['EMAIL_USERNAME']`.

If `FLASK_DEBUG` is set, only `app.config['EMAIL_USERNAME']` is used.  Customer
email addresses are ignored.

Be sure to check the `Submit` modal dialog for confirmation on where the email
will be sent!

# Theme support
HTML rendering uses [w3.css](https://www.w3schools.com/w3css/default.asp).  We
also have built-in support for [w3.css themes](https://www.w3schools.com/w3css/w3css_color_themes.asp).  Theming is split into
two categories:
*   Site theme: Controlled by the user profile
*   Invoice themes:  
    order of precedence: invoice theme, customer theme, invoice theme in profile,
    the site theme in the user profile, and finally `app.config['INVOICE_THEME']`.

# Customer Emails
You have a case (like I do) where an invoice should be sent to multiple people.
Invoicer handles this by allowing you to use `|` in between multiple names at
a server.  For example, `mary|tim@example.com` would be expanded to
the following list of email addresses:  
    `['mary@example.com', 'tim@example.com']`
Each of these addresses will be put on the `to` line of the email.

# Deployment (WIP)
*   Make sure any DB migrations are stored:  
    `flask db migrate`
*   Push everything w/ Git
*   Remote server:
    *   Pull the project
    *   Apply DB migrations:
        `flask db upgrade`
    *   Restart the service

# Delete confirmation modals
To use the application's delete confirmation modal, you must create your form
like so:  
```
{% from "_modals.html" import render_delete_modal %}

<form...action="{{url_for(...)}}" method="POST">
    <input type="hidden" id="delete_modal_target" name="delete_modal_target" value="">
    <a class="btn btn-danger btn-fill" data-toggle="modal" data-target="#delete-modal" href="#">Delete</a>
</form>

{{ render_delete_modal() }}
{% endblock %}

{% block extrascripts %}
<script src="{{ url_for('static', filename='js/delete_modal.js') }}"></script>
{% endblock %}
```

The javascript will take care of ensuring the user types in `delete` and then
submit the form.  It finds the form by the `id="delete_modal_target"` field.
This means that we don't currently support multiple confirmations.

The endpoint can also ensure the user entered the field by doing this:
```python
    from .common import form_is_deleting
    def update(...):
        if form_is_deleting():
            # NOTE: The ``code=307`` will preserve the ``POST`` method
            return redirect(url_for('.delete', item_id=item_id), code=307)
    def delete(...):
        if request.form.get('validate_delete', '').lower() != 'delete':
            flash('Invalid delete request', 'error')
            return redirect(url_for(...))
```

You may also check the value of `#delete_modal_target`, which gets set to
`delete` if things validate:  
```python
if ('delete' in request.form.get('delete_modal_target', '')
```

# Invoices
We have 3 types of invoices:
*   Plain text.  These are submitted along with HTML when sending email.
*   Full HTML with `<link>`, `<style>`, etc.  These are based on Bootstrap 4.
*   `Premailer` converted Bootstrap 4.

The full HTML version is only used to create the PDF when submitting an invoice
through email.  The `Premailer`-converted invoice is what's displayed on the
Invoice page, and the body of the submit email.

The reason why we "pre processed" the invoice using `Premailer` is because that
process takes tens of seconds.  By having it already converted, we speed
everything up by quite a bit.

The downside, of course, is that changes need to take place in both places.
Suggestion: Do the changes in the full BS4 version, then store a Premailer
version, then hack that to work.

The upside is that the invoice the users sees on `/invoice` is the exact same
HTML that goes into the body of the email.  If something's not right, the user
should notice right away.

# fail2ban
Inside the 'conf' folder you'll find a subfolder for `fail2ban` configuration.
The log file that gets parsed is `invoicer.logger.AUTH_LOG`.  This defaults
to `/var/log/invoicer/auth.log`.  This makes it easy to search for bad people.

# Caching
Invoicer supports caching through `Flask-Caching`.  The default is to use
`CACHE_TYPE = 'simple'`.  You can modify this by changing `CACHE_CONFIG` in
`instance/application.cfg`.

For example, to use `memcached`:  
```python
CACHE_CONFIG = {
    'CACHE_TYPE': 'memcached',
    'CACHE_MEMCACHED_SERVERS': ('127.0.0.1',),
    'CACHE_KEY_PREFIX': 'invoicer-',
    'CACHE_DEFAULT_TIMEOUT': 300
}
```

NOTE: You can install `python-memcached` along with invoicer by using some
version of `pip install .[memcached]`.

# Password storage
Password hashes are stored in the `User` model using
[Argon2](https://argon2-cffi.readthedocs.io/en/stable/).  The default options
will be used unless you specify different options in `instance/application.cfg`.

To modify some or all of the options, use this data structure:
```python
ARGON2_CONFIG = {
    'time_cost': 10,
    # 'memory_cost': 512,
    # 'parallelism': 2,
    # 'hash_len': 16,
    # 'salt_len': 16
}
```
This will be passed to the `argon2.PasswordHasher()` contructor.

You can also change these settings at a later point in time (e.g. to increase
complexity).  If you change them in your application, be sure to use the
`flask rehash-passwords` CLI command.  This will set a bit in the `User` model
that will tell the application to re-hash the user's password and store it in
the database.  This will only occur once.

See the `argon2_cffi` documentation for some recommendations:
https://argon2-cffi.readthedocs.io/en/stable/cli.html

# Two Factor Authentication
2FA is provided by `pyotp` and `Flask-QRCode`.  Users can enable/disable 2FA
from the profile page.

# Adding Users
I purposefully let out registration and user management.  The only supported
way of adding users is by using `flask add-user`.