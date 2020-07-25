import React from 'react';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import {
  CssBaseline, AppBar, Toolbar, ThemeProvider,
} from '@material-ui/core';
import {
  BrowserRouter as Router, Route, Switch, Redirect,
} from 'react-router-dom';
import { CookiesProvider } from 'react-cookie';
import theme from './theme';
import InitForm from './components/InitForm';
import CCForm from './components/CCForm';
import Error from './components/Error';

import AuthorizationForm from './components/AuthorizationForm';
import Create from './components/Create';
import DefaultDocs from './components/DefaultDocs';

export default function App() {
  return (
    <CookiesProvider>
      <Router>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <AppBar position="relative">
            <Toolbar>
              <Typography variant="h6" color="inherit" noWrap>
                Cookiecutter Creator
              </Typography>
            </Toolbar>
          </AppBar>
          <Container component="main" maxWidth="sm">
            <CssBaseline />
            <Switch>
              <Route path="/created">
                <Create />
              </Route>
              <Route path="/create">
                <CCForm />
              </Route>
              <Route path="/authorize">
                <AuthorizationForm />
              </Route>
              <Route path="/default-docs">
                <DefaultDocs />
              </Route>
              <Route path="/error">
                <Error />
              </Route>
              <Route exact path="/">
                <InitForm />
              </Route>
              <Route>
                <Redirect to="/authorize" />
              </Route>
            </Switch>
          </Container>
        </ThemeProvider>
      </Router>
    </CookiesProvider>
  );
}
