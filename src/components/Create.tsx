import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import {
  Grid, LinearProgress, Container, Link, Card, CardContent,
} from '@material-ui/core';
import { useLocation, useHistory } from 'react-router-dom';
import theme from '../theme';
import workerURL from '../constants';

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
    padding: '20px',
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
  const [repoOutput, setRepoOutput] = useState({ url: '', output: '' });
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
      history.push('/');
      return;
    }
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ccState),
    };
    if (!created && ccState) {
      fetch(`${workerURL}/create`, requestOptions)
        .then((response) => {
          if (!response.ok) {
            throw response;
          }
          return response.json();
        })
        .then((newData) => {
          setCreated(true);
          setRepoOutput(newData);
          history.replace(location.pathname, { ...location.state, created: true });
        })
        .catch((error) => {
          error.json().then((data: any) => {
            history.replace('/error', data);
          });
        });
    }
  },
  [created, location, setCreated, history, repoOutput, setRepoOutput]);
  const { repo = '', org = '' } = location.state || {};
  const component = created ? (
    <Card className={classes.root}>
      <CardContent>
        <Typography variant="h5">
          Successfully created
          {' '}
          <Link href={repoOutput.url}>
            {org}
            /
            {repo}
          </Link>
        </Typography>
        {(repoOutput.output !== ''
          ? (
            <>
              <Typography color="textSecondary">
                <br />
                Output from the cookiecutter:
              </Typography>
              <Typography variant="body2" style={{ whiteSpace: 'pre-line', wordBreak: 'break-word' }}>
                <br />
                {repoOutput.output}
              </Typography>
            </>
          ) : null)}
      </CardContent>
    </Card>
  ) : (
    <div className={classes.root}>
      <Typography component="h1" variant="h6">
        Please wait while your repository is being generated...
      </Typography>

      <LinearProgress color="secondary" />
    </div>
  );

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
