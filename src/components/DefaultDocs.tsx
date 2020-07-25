import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {
  Grid, Container, List, ListItem, ListItemText, Link, Card, CardContent, CardHeader,
} from '@material-ui/core';
import { useLocation, useHistory } from 'react-router-dom';
import theme from '../theme';

const useStyles = makeStyles((theme) => ({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  root: {
    padding: '20px',
    width: '100%',
    '& > * + *': {
      marginTop: theme.spacing(2),
    },
  },
}));

export default function DefaultDocs() {
  const classes = useStyles(theme);
  const location = useLocation<any>();
  const parameters = location.state;
  const history = useHistory();
  if (!location.state) {
    history.push('/');
    return null;
  }
  const ccDefaults = encodeURI(JSON.stringify(parameters.ccKeys.filter((key: any) => !key.startsWith('_')).reduce((defaults: any, key: any) => ({ ...defaults, [key]: '' }), {}), null, 2));
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
            <CardHeader title="Instructions to add default prompts" />
            <CardContent>
              <List component="nav" className={classes.root} aria-label="mailbox folders">
                <ListItem>
                  <ListItemText>
                    1. Create a repository called
                    {' '}
                    <span style={{ color: 'orangered' }}><Link href={`https://${parameters.baseUrl}/${parameters.org}/.github`}>.github</Link></span>
                    {' '}
                    under
                    {' '}
                    <span style={{ color: 'orangered' }}><Link href={`https://${parameters.baseUrl}/${parameters.org}`}>{parameters.org}</Link></span>
                    {' '}
                    if it doesn't already exist.
                  </ListItemText>
                </ListItem>
                <ListItem>
                  <ListItemText>
                    2.
                    {' '}
                    <span style={{ color: 'red' }}><Link href={`https://${parameters.baseUrl}/${parameters.org}/.github/new/master/cookiecutter/${parameters.template}/cookiecutter.json?filename=cookiecutter.json&value=${ccDefaults}&message=Create defaults for ${parameters.template} for CookieS`}>Click here</Link></span>
                    {' '}
                    to create a file called
                    {' '}
                    <span style={{ color: 'grey' }}>cookiecutter.json</span>
                    {' '}
                    in the above repository under the path
                    {' '}
                    <span style={{ color: 'grey' }}>
                      cookiecutter/
                      {parameters.template}
                    </span>
                    .
                  </ListItemText>
                </ListItem>
                <ListItem>
                  <ListItemText>
                    3. Put the default values that you want in the above file, corresponding to the
                    {' '}
                    <span style={{ color: 'red' }}>
                      <Link href={`https://${parameters.baseUrl}/${parameters.templateRepo}/blob/master/${parameters.templateDir ? `${parameters.templateDir}/` : ''}cookiecutter.json`}>
                        {parameters.template}
                        's
                      </Link>
                    </span>
                    {' '}
                    prompts.
                  </ListItemText>
                </ListItem>
                <ListItem>
                  <ListItemText>
                    Note: All the values in the above file that you are creating must be JSON strings.
                  </ListItemText>
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Container>
    </div>
  );
}
