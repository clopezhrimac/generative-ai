# SQL Talk: Natural Language to BigQuery with Gemini's Function Calling

## Overview

This app demonstrates the power of
[Gemini's Function Calling](https://cloud.google.com/vertex-ai/docs/generative-ai/multimodal/function-calling)
capabilities, enabling users to query and understand their
[BigQuery](https://cloud.google.com/bigquery) databases using natural language.
Forget complex SQL syntax – interact with your data conversationally.


## Run and modify the app in Cloud Shell Editor

After you've tried out the live demo app, you can also run your own version of
the SQL Talk app and make changes to the live app using the Cloud Shell Editor
in your own Google Cloud project.

[Open this repository and the sample app in the Cloud Shell
Editor](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/clopezhrimac/generative-ai.git&cloudshell_workspace=gemini/function-calling/sql-talk-app/&cloudshell_tutorial=tutorial.md&cloudshell_open_in_editor=app.py),
then follow the steps displayed in the tutorial in the sidebar.

## (Optional) Deploy the app to Cloud Run

When deploying this app to Cloud Run, a best practice is to [create a service
account](https://cloud.google.com/iam/docs/service-accounts-create) to attach
the following roles to, which are the permissions required for the app to read
data from BigQuery, run BigQuery jobs, and use resources in Vertex AI:

- [BigQuery Data Viewer](https://cloud.google.com/bigquery/docs/access-control#bigquery.dataViewer) (`roles/bigquery.dataViewer`)
- [BigQuery Job User](https://cloud.google.com/bigquery/docs/access-control#bigquery.jobUser) (`roles/bigquery.jobUser`)
- [Vertex AI User](https://cloud.google.com/vertex-ai/docs/general/access-control#aiplatform.user) (`roles/aiplatform.user`)

To deploy this app to
[Cloud Run](https://cloud.google.com/run/docs/deploying-source-code), run the
following command to have the app built with Cloud Build and deployed to Cloud
Run, replacing the `service-account` and `project` values with your own values,
similar to:

```shell
gcloud run deploy sql-talk --allow-unauthenticated --region us-central1 --service-account SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com --source .
```

