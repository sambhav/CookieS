import React from 'react';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import {
  CssBaseline, AppBar, Toolbar, ThemeProvider,
} from '@material-ui/core';
import theme from './theme';
import InitForm from './components/InitForm';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';

export default function App() {
  return (
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
            <Route path="/create">
            </Route>
            <Route path="/">
              <InitForm />
            </Route>
          </Switch>
        </Container>
      </ThemeProvider>
    </Router >
  );
}
