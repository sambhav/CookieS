import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Alert, AlertTitle } from '@material-ui/lab';
import {
  Grid, Container, Card, CardContent, Typography,
} from '@material-ui/core';
import { useLocation } from 'react-router-dom';
import theme from '../theme';

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

export default function Error() {
  const classes = useStyles(theme);
  const location = useLocation<any>();

  return (
    <div className={classes.paper}>
      <Container>
        <Grid
          container
          direction="column"
          justify="space-between"
          alignItems="center"
        >
          <Card className={classes.root}>
            <CardContent>
              <Alert severity="error" variant="outlined">
                <AlertTitle>Error occured during cookiecutter execution</AlertTitle>
              </Alert>
              {(location.state.detail !== ''
                ? (
                  <>
                    <Typography color="textSecondary">
                      <br />
                      Output from the cookiecutter:
                    </Typography>
                    <Typography variant="body2" style={{ whiteSpace: 'pre-line', wordBreak: 'break-word' }}>
                      <br />
                      {location.state.detail}
                    </Typography>
                  </>
                ) : null)}
            </CardContent>
          </Card>
        </Grid>
      </Container>
    </div>
  );
}
