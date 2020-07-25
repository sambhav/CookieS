import React, { useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { Button } from '@material-ui/core';
import { useForm } from 'react-hook-form';
import { useLocation, useHistory } from 'react-router-dom';
import { useCookies } from 'react-cookie';
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
}));

function useQuery() {
  return new URLSearchParams(useLocation().search);
}

interface Inputs { }

export default function AuthorizationForm() {
  const classes = useStyles(theme);
  const { handleSubmit } = useForm<Inputs>({ reValidateMode: 'onSubmit' });
  const history = useHistory();
  // eslint-disable-next-line
  const [cookies, setCookie] = useCookies();
  const onSubmit = (data: any) => {
    fetch(`${workerURL}/oauth-url`)
      .then((response) => response.json())
      .then((data) => {
        window.location.replace(data.url);
      });
  };
  const code = useQuery().get('code');
  useEffect(() => {
    if (code) {
      fetch(`${workerURL}/oauth-token/${code}`)
        .then((response) => response.json())
        .then((data) => {
          setCookie('token', data.token, { maxAge: 60 * 60 * 24 });
          history.push('/');
        });
    }
  },
  [code, history, setCookie]);

  return (
    <div className={classes.paper}>
      <Typography component="h1" variant="h5">
        Please login via Github to continue.
      </Typography>
      <form className={classes.form} onSubmit={handleSubmit(onSubmit)}>
        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          className={classes.submit}
        >
          Authorize
        </Button>
      </form>
    </div>
  );
}
