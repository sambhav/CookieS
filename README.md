# web-cc

Web-CC is Cookiecutter as a service. It spins up a web server that is able to discover
and register Github repostiories tagged with `cookiecutter` in their topics. It can
then dynamically generate forms mirroring the inputs required for the cookiecutter creation
and finally create a Github repository with the output. It also supports default values
for cookiecutters based on user specified organizations.

## Server Docs

### Development setup

1. Install [poetry.](https://python-poetry.org/docs/)
2. Change the directory to `server` and run the following commands.
3. Run `poetry env use python3.7` in this directory.
4. Run `poetry install`
5. Start the server with `uvicorn server.api:app --reload`

### Server documentation

You can view the documentation and play with the auto-generated
swagger UI at - `http://localhost:8000/docs`

### User configuration variables

The web-cc is configured via environment variables. The configurable options are -

```python
# USER CONFIG
# Token for the role account. Note: This is a secret value
# and should not be checked in. This is a required config.
WEB_CC_TOKEN
# Github API host name. Useful for GHE usage. Default: ""
WEB_CC_GITHUB_HOST_NAME
# Github base url. Useful for GHE usage. Defaults to public Github
WEB_CC_GITHUB_BASE_URL
# Role account username for use by the backend. Defaults to the username `samj1912`
WEB_CC_BOT_NAME
# Role account email for use by the backend.
# Will be used to create commits. Defaults to the mail address `sambhavs.email@gmail.com`
WEB_CC_BOT_MAIL
```

## Client Docs

In the project directory, you can run:

#### `yarn start`

Runs the app in the development mode.<br />
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.<br />
You will also see any lint errors in the console.

#### `yarn test`

Launches the test runner in the interactive watch mode.<br />
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

#### `yarn build`

Builds the app for production to the `build` folder.<br />
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.<br />
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.

#### `yarn eject`

**Note: this is a one-way operation. Once you `eject`, you can’t go back!**

If you aren’t satisfied with the build tool and configuration choices, you can `eject` at any time. This command will remove the single build dependency from your project.

Instead, it will copy all the configuration files and the transitive dependencies (webpack, Babel, ESLint, etc) right into your project so you have full control over them. All of the commands except `eject` will still work, but they will point to the copied scripts so you can tweak them. At this point you’re on your own.

You don’t have to ever use `eject`. The curated feature set is suitable for small and middle deployments, and you shouldn’t feel obligated to use this feature. However we understand that this tool wouldn’t be useful if you couldn’t customize it when you are ready for it.
