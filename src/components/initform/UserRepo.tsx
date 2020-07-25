import React from 'react';
import { Grid, TextField } from '@material-ui/core';

const UserRepo = ({ inputRef, errors }: any) => (
  <>
    <Grid item xs={12}>
      <TextField
        variant="outlined"
        required
        fullWidth
        inputRef={inputRef}
        helperText={errors?.org ? errors?.org.message : 'Name of your organization'}
        id="org"
        label="Organization"
        name="org"
        error={!!errors?.org}
        autoComplete="org"
      />
    </Grid>
    <Grid item xs={12}>
      <TextField
        variant="outlined"
        required
        fullWidth
        inputRef={inputRef}
        id="repo"
        helperText={errors?.repo ? errors?.repo.message : 'Name of the repository your wish to create'}
        label="Repository"
        name="repo"
        error={!!errors?.repo}
        autoComplete="repo"
      />
    </Grid>
  </>
);

export default UserRepo;
