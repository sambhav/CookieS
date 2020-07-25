import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import { Grid, Button } from '@material-ui/core';
import { useForm, Resolver } from 'react-hook-form';
import axios from 'axios';
import { useHistory, Redirect } from 'react-router-dom';
import Cookies from 'universal-cookie';
import { useCookies } from 'react-cookie';
import theme from '../theme';
import CookieCutterTemplate from './initform/CookieCutterTemplate';
import UserRepo from './initform/UserRepo';
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

type Inputs = {
  template: string;
  directory?: string;
  org: string;
  repo: string;
};

const getUrl = (org: string, repo: string) => {
  const cookies = new Cookies();
  return `${workerURL}/validate/${org}/${repo}?token=${cookies.get('token')}`;
};

const resolver: Resolver<any> = async (values) => {
  const { data }: any = await axios.get(getUrl(values.org, values.repo));
  const errors: any = {};
  if (data?.org) {
    errors.org = {
      type: 'validate',
      message: data.org,
    };
  }
  if (data?.repo) {
    errors.repo = {
      type: 'validate',
      message: data.repo,
    };
  }
  return {
    values: {
      template: {
        repo: values.template.split('/').slice(0, 2).join('/'),
        directory: values.template.split('/')[2] || '',
      },
      repo: values.repo,
      org: values.org,
    },
    errors,
  };
};

export default function InitForm() {
  const classes = useStyles(theme);
  const { register, handleSubmit, errors } = useForm<Inputs>({ resolver, reValidateMode: 'onSubmit' });
  const history = useHistory();
  const [cookies] = useCookies();
  if (!cookies.token) {
    return <Redirect to="/authorize" />;
  }
  const onSubmit = (data: any) => {
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...data, token: cookies.token }),
    };
    fetch(`${workerURL}/form`, requestOptions)
      .then((response) => response.json())
      .then((data) => history.push('/create', data));
  };

  return (
    <div className={classes.paper}>
      <Typography component="h1" variant="h5">
        Select your cookiecutter
      </Typography>
      <form className={classes.form} onSubmit={handleSubmit(onSubmit)}>
        <Grid container spacing={2}>
          <CookieCutterTemplate inputRef={register} />
          <UserRepo inputRef={register} errors={errors} />
        </Grid>
        <Button
          type="submit"
          fullWidth
          variant="contained"
          color="primary"
          className={classes.submit}
        >
          Initialize
        </Button>
      </form>
    </div>
  );
}
