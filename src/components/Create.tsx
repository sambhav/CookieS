import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { Button, CircularProgress, Grid, LinearProgress, Container } from '@material-ui/core';
import { useForm } from 'react-hook-form';
import theme from '../theme';
import { useLocation, useHistory } from 'react-router-dom';
import { useCookies } from 'react-cookie';


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
  const [created, setCreated] = useState(0);

  useEffect(() => {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(
        {
          ...location.state,
        }
      ),
    };
    if (created == 0) {
      setCreated(1);
      fetch('http://localhost:8000/create', requestOptions)
        .then((response) => response.json())
        .then((newData) => {
          setCreated(2);
        });
    }
  });
  const component = created == 1 ? (<div className={classes.root}>
    <Typography component="h1" variant="h6">
      Please wait while you repository is being generated...
          </Typography>

    <LinearProgress color="secondary" />
  </div>) : (
      <Button
        variant="contained"
        color="primary"
      >
        Successfully created
      </Button>);

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
