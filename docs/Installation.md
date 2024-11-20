# 🌐 Installation

Ausonia is set up to be ran through a series of Docker Containers. The following services will
be ran when the Bot is fired up:

- `postgresql_db`: A PostgreSQL Database that will be used to store any data relating to servers
and users that Ausonia may required.
- `api`: The API Server that will be used to handle AI Image Generation requests.
- `bot`: The Discord Bot itself.

The large majority of the setup procedure will be performed by the Docker Containers themselves,
however, you will need to go through some setup steps in order to ensure that Ausonia will
accommodate to your needs.

## 👣 Steps

First, you will need to verify that you have Docker installed. You may do this through running the `hello-world`
container:
```shell
docker run hello-world
```

If you have Docker installed, you should have a message that begins with something like `Hello from Docker!`. If
the command fails to run, please consult the Installation Documentation for Docker by clicking
[here](https://docs.docker.com/engine/install/). Once you've ensured that you have Docker installed, come back to
this guide.

Now that's out of the way, we can move onto the configuration part. If you head into the `config` directory, you'll
notice that there are a series of files with the suffix `.example.json`. Please duplicate or rename these files to
remove the `.example` part of the filename. At the moment, there is only one file that needs to be configured, however,
this may change with further development.

Within the **Core Configuration**, the following variables need to be defined:
- **Bot Token:** The token given by Discord to run your bot.
- **Server ID:** The ID of the Server that you intend to use your bot in.
- **Owner ID:** The User ID of the Discord User you'd like to be "Owner". This is required so that
you may run Owner Only commands.
- **NSFW Threshold:** This is a decimal value representing the minimum confidence rate that is
required by the Inappropriate Content Detector in order to consider an image NSFW. You can
experiment with this value, however, it's generally good to have this at about 0.4 to 0.6, which
is a range of 40% to 60% confident.

Once you've configured the **Core Configuration**, you may then move onto the configuration of the API. The API
Service is going to be what handles the AI Image Generation requests. A script is provided in the `api` directory,
named `create_config.py`, which will automatically create a configuration file for you based on the models you'd
like to use. Before running the script, navigate to the `api` directory and then the `models` directory, where you
will need to place the models that you would like to use. Please note that the models must be in the `.safetensors`
format. Once you've made sure that you have all the models that you want to use, run the script like so:
```shell
python3 create_config.py
```

After the configuration has been created, access the configuration file in the `api` directory. The configuration
file will be named `config.json`. Go through each entry in the file and ensure that you update the `pipeline`, 
`is_nsfw` and, if you wish, the `name` field. Once you have made sure that the configuration file is correct, you
can then move onto the configuring your `.envrc` file.

Duplicate the `.envrc.example` file and rename it to `.envrc`. Once you've done this, open the file and ensure that
the `DB_PASSWORD` variable is set to the password that you want to use for your PostgreSQL Database. After that,
head to the [HuggingFace](https://huggingface.co) website and obtain a Read Access Token. Finally, set the
`AUTH_TOKEN` variable in your `.envrc` file to the token that you obtained.

You should then be good to run the bot:
```shell
docker compose up # Add -d if you want the bot to run in the background
```

## 🔩 Optional Stuff

This section contains things that are good to know during the installation process but are not necessarily things
that you are *required* to do.