# What is it?

This project makes it simple to authenticate against a Veracode API that is using HMAC auth.

# As a Veracode **customer**, I want to call new Veracode APIs

Here are some usage examples to show you what this is about. They all assume you've installed
and set up this library. We will explain how to do that later in this README.

## Clean command-line calls with a popular tool

When you install this library, you will get a plugin for [`requests`](http://docs.python-requests.org/en/latest/)
and a plugin for [`httpie`](https://github.com/jkbrzt/httpie). The `requests` plugin is explained
further down. First, let's look at using HTTPie:

    $ http --auth-type=veracode_hmac "https://api.veracode.com/appsec/v1/applications"

That's it! Doing the above will load credentials from the proper location,
generate an HMAC `Authorization` header, and issue an HTTPS call 
to a Veracode API. 

You can use a short argument for `--auth-type`:

    $ http -A veracode_hmac "https://api.veracode.com/appsec/v1/applications"
    
Calls to other API endpoints will look very similar. The default HTTP Method is `GET`
but other methods are simple to use. Here are some rapid examples:

    $ http --auth-type=veracode_hmac "https://api.veracode.com/appsec/v1/applications"
    $ http --auth-type=veracode_hmac POST "https://api.veracode.com/foo/bar" < ./foo.json

What else can you do? Just check `http --help` and
[view the HTTPie documentation](https://github.com/jkbrzt/httpie). 
HTTPie is an open-source tool with extremely strong community support, great flexibility,
and great documentation. The auth aspect won't vary: the plugin will "just work." All
the other varying aspects will be particular to the API the user is calling, and the user
can read the docs we provide about our APIs to answer those questions.

## Lower-level command-line usage

You can create raw signatures like so. (This does not make a call to anywhere on the internet,

    $ veracode_hmac_auth GET https://api.veracode.com/appsec/v1/applications
    VERACODE-HMAC-SHA-256 ...

    # scheme is optional, https is assumed. (error thrown for other schemes.)
    $ veracode_hmac_auth GET api.veracode.com
    VERACODE-HMAC-SHA-256 ...
    
    $ veracode_hmac_auth GET https://api.veracode.com/appsec/v1/applications
    VERACODE-HMAC-SHA-256 ...

Then you would need to copy/paste this signature very carefully, and use with `curl`,
`httpie`, or something like Postman. But HMAC is robust, and it's
easy to mess up a character or two when doing copy-and-paste.
 
There is a better way! Just pipe the output. Here's an example with `curl`:

    $ URL='https://api.veracode.com/appsec/v1/applications'
    $ curl --header "Authorization: $(veracode_hmac_auth GET $URL | tr '\r\n' ' ')" $URL

(It is important to remember the `| tr '\r\n' ' '` snippet. This is a mitigation to protect against
[CRLF Injection](http://www.veracode.com/security/crlf-injection). 

This will work too, if you like [`httpie`](https://github.com/jkbrzt/httpie), the popular
`curl` alternative.

    $ http --verbose GET $URL "Authorization:$(veracode_hmac_auth GET $URL | tr '\r\n' ' ')"
    
## Calling the APIs from Python code

It's very easy to sign API calls you're making, as long as you are using the 
[`requests`](http://docs.python-requests.org/en/latest/) library.
(If you're not using the requests module, you should be. Other libraries will not be supported.)


It is easy though! Simply add
`auth=RequestsAuthPluginVeracodeHMAC()` to your call to requests 

    from veracode_api_signing.plugin_requests import RequestsAuthPluginVeracodeHMAC
    ...
    requests.get(api_url, auth=RequestsAuthPluginVeracodeHMAC()) 

By default, this class will load credentials from the filesystem or environment variables,
as you have configured.

If you have your API credentials somewhere non-standard (like a database), you can get them,
and pass them in as explicit arguments. They will be honored.

    requests.get(api_url, auth=RequestsAuthPluginVeracodeHMAC(api_key_id=<YOUR_API_KEY_ID>, api_key_secret=<YOUR_API_KEY_SECRET>))
 

--------------------------------------

# Setup

## Requirements

1. A set of Veracode credentials
2. Python 3.9 or greater.
3. [Pip](https://pip.pypa.io/en/latest/). Pip may already be installed. To confirm  Install Pip [using an OS Package Manager](https://pip.pypa.io/en/latest/installing.html#using-os-package-managers) 
   or by [using a Python script](https://pip.pypa.io/en/latest/installing.html#install-pip) 

## How to Check Pip and Python Version
	$ python --version
	Python 3.9.10
	$ pip --version
	pip 22.0.4 from /usr/local/lib/python3.9/site-packages/pip (python 3.9)
## Installation

Install this project from PyPi

    $ pip install veracode-api-signing

### Troubleshooting
 
- Windows users take note: whenever you create a folder starting with a dot (`.`), you should use the
`mkdir` command. [If you try to use Windows Explorer, the `dir` command, there are caveats.
 Click for more details if you're having trouble.](http://superuser.com/a/483763/122249))

### Set up credentials

Set up your Veracode credentials. You can put them in your environment or you can put them in a credentials
file.

To put them in your environment variables, set the following variables by running something like
 
    $ export VERACODE_API_KEY_ID=<your_api_key_id> 
    $ export VERACODE_API_KEY_SECRET=<your_api_key_secret> 

If you do not want to put them in your environment variables, you may create a `~/.veracode/credentials` file like
the following

    [default]
    veracode_api_key_id = <YOUR_API_KEY_ID>
    veracode_api_key_secret = <YOUR_API_KEY_SECRET>

### Secure your credentials file

If you used a credentials file, we recommend you set the file's permissions to 
make sure that only the owner is allowed to
access the file. In Linux, use `chmod 600` to set owner-only permissions. In Windows,
use the [Properties window](http://technet.microsoft.com/en-us/library/cc772196.aspx)
or use the [icacls](http://technet.microsoft.com/en-us/library/cc753525%28WS.10%29.aspx) command.

### Using multiple profiles

If you need to store multiple sets of credentials, such as for different environments,
or different accounts corresponding to different customers you may work with ... you can!

If you're using the config file, you can define multiple profiles.

    [default]
    veracode_api_key_id = <YOUR_API_KEY_ID>
    veracode_api_key_secret = <YOUR_API_KEY_SECRET>
    
    [stage]
    veracode_api_key_id = <YOUR_STAGE_API_KEY_ID>
    veracode_api_key_secret = <YOUR_STAGE_API_KEY_SECRET>

    [qa]
    veracode_api_key_id = <YOUR_QA_API_KEY_ID>
    veracode_api_key_secret = <YOUR_QA_API_KEY_SECRET>
    
By default, the `default` profile will still be used. Set `VERACODE_API_PROFILE` to change
profiles. For example, if you wanted to use `stage` in bash (etc.), you would do...

	$ export VERACODE_API_PROFILE=stage

In bash (etc.) you can also set environment variables per command, making it very easy
to use this environment variable like a parameter.

	VERACODE_API_PROFILE=stage http -A veracode_hmac https://api.veracode.com/appsec/v1/applications

This will work on Linux, Mac, and Windows, as long as you are using bash or something similar.

On Windows DOS Prompt you would use `SET`. It's not straightforward to set per-command though.
(If this is limiting you, consider using cygwin or git bash.)
