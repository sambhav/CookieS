import React, { useState, useEffect } from "react";
import { Grid, TextField } from "@material-ui/core";
import Autocomplete from "@material-ui/lab/Autocomplete";

interface Cookiecutters {
  [key: string]: string[]
}

const CookiecutterTemplate = ({ inputRef }: any) => {
  const [cookiecutters, setCookiecutters] = useState<Cookiecutters>({});
  useEffect(() => {
    if (Object.keys(cookiecutters).length === 0) {
      fetch("http://localhost:8000/cookicutters")
        .then(response => response.json())
        .then((data) => setCookiecutters(data.cookiecutters))
    }
  })
  const [directories, setDirectories] = useState<string[]>([]);
  const handleDirectory = (_: any, value: string | null) => {
    setDirectories(value === null ? [] : cookiecutters[value] || []);
  }
  return (
    <>
      <Grid item xs={12}>
        <Autocomplete
          id="template"
          options={Object.keys(cookiecutters)}
          getOptionLabel={(option) => option}
          onChange={handleDirectory}
          renderInput={(params) => <TextField {...params}
            required
            inputRef={inputRef}
            autoComplete="template"
            name="template"
            helperText="Cookiecutter template repository"
            label="Cookiecutter" variant="outlined" />}
        />
      </Grid>
      {
        (
          directories.length !== 0 ?
            <Grid item xs={12}>
              <Autocomplete
                id="directory"
                options={directories}
                getOptionLabel={(option) => option}
                renderInput={
                  (params) =>
                    <TextField {...params}
                      required
                      inputRef={inputRef}
                      name="directory"
                      helperText="Cookiecutter template subdirectory"
                      autoComplete="directory"
                      label="Directory" variant="outlined" />}
              />
            </Grid> :
            null
        )
      }
    </>
  )
}

export default CookiecutterTemplate;
