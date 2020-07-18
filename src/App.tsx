import React from 'react';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import {
  CssBaseline, AppBar, Toolbar, ThemeProvider,
} from '@material-ui/core';
import theme from './theme';
import InitForm from './components/InitForm';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import CCForm from './components/CCForm';

import { CookiesProvider } from 'react-cookie';
import AuthorizationForm from './components/AuthorizationForm';
import Create from './components/Create';


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
              <Route path="/">
                <InitForm />
              </Route>
            </Switch>
          </Container>
        </ThemeProvider>
      </Router >
    </CookiesProvider>
  );
}
