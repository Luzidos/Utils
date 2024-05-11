Everytime we get a new user:
- we need to go to GCP -> IAM & Admin -> Service Accounts and create a new service account
- grant owner permissions
- download json key
- upload to user dir in s3 as `service_account.json`
