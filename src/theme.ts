import { createMuiTheme } from "@material-ui/core";
import { red, deepOrange } from "@material-ui/core/colors";

const theme = createMuiTheme({
    palette: {
        primary: red,
        secondary: deepOrange,
        type: 'dark',
    },
});

export default theme;
