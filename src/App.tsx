import React from 'react';
import Container from '@material-ui/core/Container';
import Typography from '@material-ui/core/Typography';
import { CssBaseline, AppBar, Toolbar, ThemeProvider } from '@material-ui/core';
import theme from "./theme";
import InitForm from "./components/InitForm";

export default function App() {
  return (
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
        <InitForm />
      </Container>
    </ThemeProvider>
  );

}
