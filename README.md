# ![image](https://user-images.githubusercontent.com/16130816/87261930-09725f00-c4b0-11ea-986b-fef3a4d1b529.png) CookieS ![image](https://user-images.githubusercontent.com/16130816/87261894-e3e55580-c4af-11ea-9d60-49dee1b35b21.png)


CookieS is a Cookiecutter as a Service platform. It spins up a web server that is able to discover
and register Github repositories tagged with `cookiecutter` in their topics. It can
then dynamically generate forms mirroring the inputs required for the cookiecutter creation
and finally create a Github repository with the output. It also supports default values
for cookiecutters based on user specified organizations.

# Demo
Here is a demo of the web UI with the pypackage cookiecutter. Notice how it loadde the defaults from the .github repository
of the user-specified org.

![cookiecutter-demo](https://user-images.githubusercontent.com/16130816/87864056-13d2a400-c95b-11ea-9452-9bc64f3d3a1a.gif)

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

CookieS back-end is configured via environment variables. The configurable options are -

```python
# USER CONFIG
# Github API host name. Useful for GHE usage.
WEB_CC_GITHUB_HOST_NAME
# Github base url. Useful for GHE usage.
WEB_CC_GITHUB_BASE_URL
# See https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/
# On how to create an OAuth app
# Github OAuth App Client ID.
WEB_CC_OAUTH_CLIENT_ID
# Github OAuth App Client Secret.
WEB_CC_OAUTH_CLIENT_SECRET
# A secret key generated via Fernet.generate_key().decode()
# Please replace the default one below to ensure that the
# tokens are passed securely between the frontend and the
# backend.
WEB_CC_APP_KEY
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

---

Icon made by Freepik from www.flaticon.com
