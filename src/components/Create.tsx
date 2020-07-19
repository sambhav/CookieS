import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { Button, Grid, LinearProgress, Container, Paper, Link, } from '@material-ui/core';
import theme from '../theme';
import { Alert, AlertTitle } from '@material-ui/lab';
import { useLocation, useHistory } from 'react-router-dom';
import { report } from 'process';


const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  form: {
    width: '100%',
    marginTop: theme.spacing(3),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
  root: {
    padding: "20px",
    width: '100%',
    '& > * + *': {
      marginTop: theme.spacing(2),
    },
  },
}));

export default function Create() {
  const classes = useStyles(theme);
  const location = useLocation<any>();
  // Check the location state if the cookiecutter has been created already.
  const [created, setCreated] = useState(location.state?.created || false);
  const history = useHistory();
  useEffect(() => {
    // We copy the location state
    // and in case we don't have anything in
    // it except for the `created` flag
    // we redirect the user to the homepage
    // This is to avoid accidental refreshes recreating
    // the cookiecutter
    const { ...ccState } = location.state || {};
    delete ccState.created;
    if (!Object.keys(ccState).length) {
      history.push("/");
      return;
    }
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ccState),
    };
    if (!created && ccState) {
      fetch('http://localhost:8000/create', requestOptions)
        .then((response) => response.json())
        .then((newData) => {
          setCreated(true);
          history.replace(location.pathname, { ...location.state, created: true });
        });
    }
  },
    [created, location, setCreated, history]
  );
  const { repo = "", org = "" } = location.state || {};
  const component = created ? (
    <Typography variant="h5">Successfully created <Link href={`https://github.com/${org}/${repo}`} >
      {org}/{repo}  </Link></Typography>
  ) : (<div className={classes.root}>
    <Typography component="h1" variant="h6">
      Please wait while your repository is being generated...
    </Typography>

    <LinearProgress color="secondary" />
  </div>);

  return (
    <div className={classes.paper}>
      <Container>
        <Grid
          container
          direction="column"
          justify="space-between"
          alignItems="center"
        >

          {component}
        </Grid>
      </Container>
    </div>
  );
}
