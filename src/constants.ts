const workerURL : string = (
    process.env.REACT_APP_WORKER_URL || "http://localhost:8000")
);

export default workerURL;
