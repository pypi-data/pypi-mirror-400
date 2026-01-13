r'''
# cdk-library-aurora-native-backup

A CDK construct library that creates and manages Docker images for Aurora PostgreSQL native backups using `pg_dump`.
The resulting images are designed for use with Amazon ECS Fargate for scalable, serverless backup operations.

## Features

* **Multi-Database Support**: Back up multiple databases from the same Aurora cluster in a single service
* **Pre-built Docker Image**: Amazon Linux 2023 base with PostgreSQL 17 client tools and AWS CLI v2
* **ECR Repository Management**: Automatically creates and manages ECR repositories with security best practices
* **Complete Backup Service**: Ready-to-use ECS Fargate service for scheduled Aurora backups
* **EFS and S3 Support**: Built-in support for backing up to EFS with S3 sync
* **Comprehensive Backup**: Uses `pg_dump` directory format for efficient storage and simplified restore
* **Production Ready**: Includes proper error handling, logging, and cleanup mechanisms
* **Secure Authentication**: Uses AWS Secrets Manager for database password management

## API Doc

See [API](API.md)

## Interface Structure

The library provides two main constructs, each with its own configuration interface:

* **`AuroraBackupRepository`** (`AuroraBackupRepositoryProps`): Manages the ECR repository and Docker image for backups.
* **`AuroraNativeBackupService`** (`AuroraNativeBackupServiceProps`): Manages the backup service infrastructure (VPC, Aurora cluster, S3 bucket, compute resources, etc.), and uses:

  * **`AuroraBackupConnectionProps`**: For database connection settings (username, database names array, password secret).

This separation allows for cleaner organization of image/repository management, connection credentials, and infrastructure settings.

## Multi-Database Support

The library supports backing up multiple databases from the same Aurora PostgreSQL cluster in a single backup service. Simply provide an array of database names in the `databaseNames` property (defaults to `['postgres']` if not specified). Each database will be backed up separately and stored in its own S3 folder structure.

## Database User Setup

Create a dedicated database user with read-only backup permissions on **ALL databases** to be backed up.

For PostgreSQL 14+ (recommended), use the built-in `pg_read_all_data` role for comprehensive read access:

```sql
-- Connect to each database and grant permissions
\c your_database_1;
GRANT CONNECT ON DATABASE your_database_1 TO backup_user;
GRANT pg_read_all_data TO backup_user;

-- Repeat for each additional database
\c your_database_2;
GRANT CONNECT ON DATABASE your_database_2 TO backup_user;
GRANT pg_read_all_data TO backup_user;
```

The `pg_read_all_data` role automatically provides:

* `SELECT` on all tables and views
* `USAGE` on all schemas
* `SELECT` and `USAGE` on all sequences
* Access to future objects without requiring additional grants

**Note**: This library requires PostgreSQL 14 or newer for the `pg_read_all_data` role.

## Shortcomings

* The backup service requires password-based authentication (no IAM database authentication for now)
* The backup container runs as a scheduled task, not continuously, so it cannot capture incremental changes
* Custom backup scripts are not currently supported, only the built-in `pg_dump` functionality
* When backing up multiple databases, if one database backup fails, the task continues with the remaining databases but the overall task does not fail - individual database backup failures must be monitored through CloudWatch logs

## Examples

### Prerequisites

To use this construct, you must have:

* An AWS CDK stack with a defined environment (account and region)
* An existing VPC for the backup service
* An existing Aurora PostgreSQL database cluster
* An AWS Secrets Manager secret containing database credentials (recommended)
* A database user with the required backup permissions (see above)

### Complete Backup Service (Recommended)

For most use cases, use the `AuroraNativeBackupService` which provides a complete, ready-to-use backup solution:

#### TypeScript

```python
import { Stack, StackProps, Duration, aws_ec2 as ec2, aws_rds as rds, aws_scheduler as scheduler, aws_secretsmanager as secretsmanager } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { AuroraNativeBackupService, AuroraBackupRepository } from '@renovosolutions/cdk-library-aurora-native-backup';

export class BackupServiceStack extends Stack {
  constructor(scope: Construct, id: string, props: StackProps) {
    super(scope, id, props);

    // Your existing Aurora PostgreSQL database cluster and VPC
    const vpc = ec2.Vpc.fromLookup(this, 'Vpc', { isDefault: true });
    const dbCluster = rds.DatabaseCluster.fromDatabaseClusterAttributes(this, 'DbCluster', {
      clusterIdentifier: 'my-production-cluster',
      clusterEndpointAddress: 'cluster.xyz.region.rds.amazonaws.com',
      port: 5432,
    });

    // First create the backup repository
    const backupRepository = new AuroraBackupRepository(this, 'BackupRepository', {
      repositoryName: 'aurora-postgres-backup',
    });

    // Secret containing the backup user's password
    const backupUserSecret = secretsmanager.Secret.fromSecretAttributes(this, 'BackupUserSecret', {
      secretArn: 'arn:aws:secretsmanager:region:account:secret:backup-user-password-abc123',
    });

    // Create the complete backup service
    const backupService = new AuroraNativeBackupService(this, 'BackupService', {
      cluster: dbCluster,
      vpc,
      backupBucketName: 'my-aurora-production-backups',
      ecrRepository: backupRepository.repository,
      connection: {
        username: 'backup_user',
        databaseNames: ['production', 'analytics', 'reporting'],
        passwordSecret: backupUserSecret,
      },
      retentionDays: 30,
      backupSchedule: scheduler.ScheduleExpression.cron({ minute: '0', hour: '2' }), // Daily at 2 AM UTC
      cpu: 1024, // Override default of 256
      memoryLimitMiB: 2048, // Override default of 512
    });
  }
}
```

#### Python

```python
from aws_cdk import (
  Stack,
  Duration,
  aws_ec2 as ec2,
  aws_rds as rds,
  aws_scheduler as scheduler,
  aws_secretsmanager as secretsmanager
)
from constructs import Construct
from cdk_library_aurora_native_backup import AuroraNativeBackupService, AuroraBackupRepository

class BackupServiceStack(Stack):
  def __init__(self, scope: Construct, id: str, **kwargs):
    super().__init__(scope, id, **kwargs)

    # Your existing Aurora PostgreSQL database cluster and VPC
    vpc = ec2.Vpc.from_lookup(self, "Vpc", is_default=True)
    db_cluster = rds.DatabaseCluster.from_database_cluster_attributes(self, "DbCluster",
      cluster_identifier="my-production-cluster",
      cluster_endpoint_address="cluster.xyz.region.rds.amazonaws.com",
      port=5432
    )

    # First create the backup repository
    backup_repository = AuroraBackupRepository(self, "BackupRepository",
      repository_name="aurora-postgres-backup"
    )

    # Secret containing the backup user's password
    backup_user_secret = secretsmanager.Secret.from_secret_attributes(self, "BackupUserSecret",
      secret_arn="arn:aws:secretsmanager:region:account:secret:backup-user-password-abc123"
    )

    # Create the complete backup service
    backup_service = AuroraNativeBackupService(self, "BackupService",
      cluster=db_cluster,
      vpc=vpc,
      backup_bucket_name="my-aurora-production-backups",
      ecr_repository=backup_repository.repository,
      connection={
        "username": "backup_user",
        "database_names": ["production", "analytics", "reporting"],
        "password_secret": backup_user_secret
      },
      retention_days=30,
      backup_schedule=scheduler.ScheduleExpression.cron(minute='0', hour='2'),  # Daily at 2 AM UTC
      cpu=1024,  # Override default of 256
      memory_limit_mi_b=2048  # Override default of 512
    )
```

## Environment Variables

All environment variables used by the backup container are set automatically by the constructs. You do not need to set them manually.

| Environment Variable   | Description                                               | CDK Prop / Source                        |
|-----------------------|-----------------------------------------------------------|------------------------------------------|
| `DB_HOST`             | Aurora PostgreSQL database cluster endpoint               | `cluster.clusterEndpoint.hostname`       |
| `DB_NAMES`            | Array of database names to backup                         | `connection.databaseNames`               |
| `DB_USER`             | Database username                                         | `connection.username`                    |
| `DB_PASSWORD`         | Database password                                         | `connection.passwordSecret`     |
| `AWS_REGION`          | AWS region                                                | `Stack.region`                           |
| `CLUSTER_IDENTIFIER`  | Cluster ID used as S3 path prefix (`backups/{CLUSTER_IDENTIFIER}/`) | `cluster.clusterIdentifier`              |
| `DB_PORT`             | Database port (default: `5432`)                           | `cluster.clusterEndpoint.port`           |
| `BACKUP_ROOT`         | Backup directory (default: `/mnt/aurora-backups`)         | (internal default)                       |
| `S3_BUCKET`           | S3 bucket for backup sync                                 | `backupBucketName`                       |
| `S3_PREFIX`           | S3 prefix (default: `backups`)                            | (internal default)                       |

## Backup Process

1. **Validation**: Checks AWS credentials and creates backup directories
2. **Database Backup**: For each database in the `DB_NAMES` array:

   * Uses `pg_dump --format=directory` with gzip compression (level 9) for each data file
   * Creates separate backup directory per database with date stamp
   * If one database backup fails, continues with remaining databases
3. **Verification**: Validates each backup contains `toc.dat` file
4. **S3 Sync**: Syncs each database backup to S3 bucket under separate database folders
5. **Cleanup**: Removes local backups after successful S3 sync

## Security Considerations

* ECR repositories created with image scanning enabled
* EFS encryption in transit supported
* IAM permissions follow principle of least privilege
* Use AWS Secrets Manager for database passwords in production
* Consider VPC endpoints for S3 to avoid internet traffic

## Backup Storage Structure

Local EFS structure (per database):

```text
/mnt/aurora-backups/
├── production/
│   └── YYYY-MM-DD/
│       ├── toc.dat                # PostgreSQL table of contents
│       ├── ####.dat.gz            # Compressed table data files
│       └── ####.dat.gz            # Additional data files
├── analytics/
│   └── YYYY-MM-DD/
│       ├── toc.dat
│       └── ####.dat.gz
└── reporting/
    └── YYYY-MM-DD/
        ├── toc.dat
        └── ####.dat.gz
```

S3 structure:

```text
s3://my-backup-bucket/
└── backups/
    └── {CLUSTER_IDENTIFIER}/
        ├── production/
        │   └── YYYY-MM-DD/
        │       ├── toc.dat
        │       └── ####.dat.gz
        ├── analytics/
        │   └── YYYY-MM-DD/
        │       ├── toc.dat
        │       └── ####.dat.gz
        └── reporting/
            └── YYYY-MM-DD/
                ├── toc.dat
                └── ####.dat.gz
```

## Restoration

### Interactive Restore CLI (Recommended)

This library includes an interactive TypeScript CLI that simplifies the restore process with auto-discovery and guided prompts:

```bash
npx ts-node restore_script/aurora-restore-cli.ts
```

**Features:**

* **Auto-discovery**: Automatically finds S3 backup buckets using the `aurora_native_backup_bucket=true` tag
* **Interactive selection**: Guided prompts for cluster, database, backup date, and tables
* **Table-level restore**: Select specific tables or restore entire database
* **Optimized downloads**: Only downloads required backup files
* **Ready-to-run commands**: Generates and optionally executes `pg_restore` commands

**Prerequisites:**

* Node.js and TypeScript installed
* AWS credentials configured (via AWS CLI, environment variables, or IAM role)
* `pg_restore` command available in your PATH
* Network access to target PostgreSQL database
* Database user with restore permissions on target database:

  * `CREATE` privilege (for creating tables, indexes, constraints)
  * `INSERT` privilege (for loading data)
  * `USAGE` and `CREATE` on schemas
  * For full database restore: `CREATEDB` privilege or superuser role

**Setup and Execution:**

First, install dependencies:

```bash
cd restore_script
yarn install
```

Then run the interactive CLI:

```bash
npx ts-node aurora-restore-cli.ts
```

The CLI will guide you through selecting your backup source, target database, and specific tables to restore.

**Workflow:**

1. **S3 Configuration**: Auto-discovers backup bucket or prompts for manual entry
2. **Source Selection**: Choose cluster, database, and backup date
3. **Table Selection**: Select specific tables or full database restore
4. **Target Configuration**: Enter target database connection details
5. **Execution**: Downloads backup files and generates restore command

### Manual Restoration

For advanced users or automation, backups are stored in S3 under organized paths:

```text
s3://my-backup-bucket/backups/{CLUSTER_IDENTIFIER}/{DATABASE_NAME}/YYYY-MM-DD/
```

**Download backup files:**

```bash
aws s3 cp --recursive s3://my-backup-bucket/backups/{CLUSTER_IDENTIFIER}/production/YYYY-MM-DD/ /path/to/backup/directory/
```

**Restore commands:**

Full database restore:

```bash
pg_restore -h target-host -U username -d target_db -v -C /path/to/backup/directory/
```

List backup contents:

```bash
pg_restore --list /path/to/backup/directory/
```

Selective table restore:

```bash
pg_restore -h target-host -U username -d target_db -v -t table_name /path/to/backup/directory/
```

## Contributing

Contributions are welcome! Please follow these guidelines to help us maintain and improve the project:

### Code Structure and Interfaces

* The main user-facing interfaces are:

  * `AuroraBackupRepositoryProps` in `src/aurora-backup-repository.ts`
  * `AuroraNativeBackupServiceProps` and `AuroraBackupConnectionProps` in `src/aurora-native-backup-service.ts`
* All constructs and their configuration interfaces are defined in the `src/` directory.

### Code Generation and Project Tasks

* This project uses [projen](https://github.com/projen/projen) for project management and code generation.
* If you make changes to the project configuration (`.projenrc.ts`), run:

  ```sh
  npx projen
  ```

  This will regenerate all managed files, including `package.json` and other configuration files.

### Building and Testing

* To build the project and run all tests, use:

  ```sh
  yarn build
  ```

  This will compile the code, run unit tests, and ensure everything is up to date.

## License

This project is licensed under the Apache License, Version 2.0 - see the [LICENSE](LICENSE) file for details.
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_ecr as _aws_cdk_aws_ecr_ceddda9d
import aws_cdk.aws_ecr_assets as _aws_cdk_aws_ecr_assets_ceddda9d
import aws_cdk.aws_ecs as _aws_cdk_aws_ecs_ceddda9d
import aws_cdk.aws_efs as _aws_cdk_aws_efs_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_rds as _aws_cdk_aws_rds_ceddda9d
import aws_cdk.aws_s3 as _aws_cdk_aws_s3_ceddda9d
import aws_cdk.aws_scheduler as _aws_cdk_aws_scheduler_ceddda9d
import aws_cdk.aws_secretsmanager as _aws_cdk_aws_secretsmanager_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aurora-native-backup.AuroraBackupConnectionProps",
    jsii_struct_bases=[],
    name_mapping={
        "password_secret": "passwordSecret",
        "username": "username",
        "database_names": "databaseNames",
    },
)
class AuroraBackupConnectionProps:
    def __init__(
        self,
        *,
        password_secret: "_aws_cdk_aws_secretsmanager_ceddda9d.ISecret",
        username: builtins.str,
        database_names: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''Database connection configuration for the Aurora backup service.

        :param password_secret: Secrets Manager secret containing the database password. Required for database authentication.
        :param username: The database username for backup operations. Must exist in the Aurora PostgreSQL database cluster with read permissions on ALL databases to be backed up. For PostgreSQL 14+ (recommended), use the pg_read_all_data role: - GRANT CONNECT ON DATABASE your_database TO backup_user; - GRANT pg_read_all_data TO backup_user; The pg_read_all_data role automatically provides SELECT on all tables/views, USAGE on schemas/sequences, and access to future objects without additional grants.
        :param database_names: The database names to backup. The backup user must have appropriate permissions on all databases in this array. Default: ['postgres'] - Uses the cluster's default database
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__373be5d587e3914f8f2c064a490876c36c34094185d72d447d8942426a1489bd)
            check_type(argname="argument password_secret", value=password_secret, expected_type=type_hints["password_secret"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument database_names", value=database_names, expected_type=type_hints["database_names"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "password_secret": password_secret,
            "username": username,
        }
        if database_names is not None:
            self._values["database_names"] = database_names

    @builtins.property
    def password_secret(self) -> "_aws_cdk_aws_secretsmanager_ceddda9d.ISecret":
        '''Secrets Manager secret containing the database password.

        Required for database authentication.
        '''
        result = self._values.get("password_secret")
        assert result is not None, "Required property 'password_secret' is missing"
        return typing.cast("_aws_cdk_aws_secretsmanager_ceddda9d.ISecret", result)

    @builtins.property
    def username(self) -> builtins.str:
        '''The database username for backup operations.

        Must exist in the Aurora PostgreSQL database cluster with read permissions on ALL databases to be backed up.

        For PostgreSQL 14+ (recommended), use the pg_read_all_data role:

        - GRANT CONNECT ON DATABASE your_database TO backup_user;
        - GRANT pg_read_all_data TO backup_user;

        The pg_read_all_data role automatically provides SELECT on all tables/views, USAGE on schemas/sequences,
        and access to future objects without additional grants.

        Example::

            'backup_user'
        '''
        result = self._values.get("username")
        assert result is not None, "Required property 'username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def database_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The database names to backup.

        The backup user must have appropriate permissions on all databases in this array.

        :default: ['postgres'] - Uses the cluster's default database
        '''
        result = self._values.get("database_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuroraBackupConnectionProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuroraBackupRepository(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aurora-native-backup.AuroraBackupRepository",
):
    '''A construct that creates and manages a Docker image for Aurora PostgreSQL native backups.

    Creates an ECR repository and builds a Docker image containing PostgreSQL 17 client tools,
    AWS CLI v2, and backup scripts. The image is designed for use with the ``AuroraNativeBackupService``
    construct in this same library.

    Example::

        const backupRepository = new AuroraBackupRepository(this, 'BackupRepository', {
          repositoryName: 'aurora-postgres-backup',
        });
        
        const backupService = new AuroraNativeBackupService(this, 'BackupService', {
          cluster: myAuroraCluster,
          vpc: vpc,
          backupBucketName: 'my-aurora-backups',
          ecrRepository: backupRepository.repository,
          connection: {
            username: 'backup_user',
            databaseNames: ['production'],
            passwordSecret: backupUserSecret,
          },
        });
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''The constructor for the AuroraBackupRepository.

        This creates an ECR repository and builds a Docker image containing PostgreSQL 17 client tools,
        AWS CLI v2, and backup scripts for Aurora PostgreSQL native backups.

        :param scope: The scope in which to create this Construct. Normally this is a stack.
        :param id: The Construct ID of the backup repository.
        :param repository_name: The name of the ECR repository to create. If not provided, CDK will generate a unique name based on the stack and construct ID. Default: CDK-generated name
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cadd1c8e90a4309ad8370d70b5c9f6c73101a7e430d62e74d6087d71baca8b4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AuroraBackupRepositoryProps(repository_name=repository_name)

        jsii.create(self.__class__, self, [scope, id, props])

    @jsii.member(jsii_name="grantPull")
    def grant_pull(
        self,
        grantee: "_aws_cdk_aws_iam_ceddda9d.IPrincipal",
    ) -> "_aws_cdk_aws_iam_ceddda9d.Grant":
        '''Grants permissions to pull images from the ECR repository.

        :param grantee: The IAM principal to grant pull permissions to.

        :return: The grant object representing the permissions granted
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25622354894e991f1a249e2cb7693232d5b2b058af8ccb5277b31f87eec94bcb)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast("_aws_cdk_aws_iam_ceddda9d.Grant", jsii.invoke(self, "grantPull", [grantee]))

    @jsii.member(jsii_name="grantPullPush")
    def grant_pull_push(
        self,
        grantee: "_aws_cdk_aws_iam_ceddda9d.IPrincipal",
    ) -> "_aws_cdk_aws_iam_ceddda9d.Grant":
        '''Grants full permissions to the ECR repository.

        :param grantee: The IAM principal to grant full permissions to.

        :return: The grant object representing the permissions granted
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4045bb29c2d773d57ae664aaf513384b2e67dfbed4ca98c1afdc621bb87ea5ba)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast("_aws_cdk_aws_iam_ceddda9d.Grant", jsii.invoke(self, "grantPullPush", [grantee]))

    @jsii.member(jsii_name="grantPush")
    def grant_push(
        self,
        grantee: "_aws_cdk_aws_iam_ceddda9d.IPrincipal",
    ) -> "_aws_cdk_aws_iam_ceddda9d.Grant":
        '''Grants permissions to push images to the ECR repository.

        :param grantee: The IAM principal to grant push permissions to.

        :return: The grant object representing the permissions granted
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04796329b3961abe09d968683c47dbc71e660bee40c2c0f4ade11e8da9ea6949)
            check_type(argname="argument grantee", value=grantee, expected_type=type_hints["grantee"])
        return typing.cast("_aws_cdk_aws_iam_ceddda9d.Grant", jsii.invoke(self, "grantPush", [grantee]))

    @builtins.property
    @jsii.member(jsii_name="imageAsset")
    def image_asset(self) -> "_aws_cdk_aws_ecr_assets_ceddda9d.DockerImageAsset":
        '''The Docker image asset containing the built backup image.'''
        return typing.cast("_aws_cdk_aws_ecr_assets_ceddda9d.DockerImageAsset", jsii.get(self, "imageAsset"))

    @builtins.property
    @jsii.member(jsii_name="imageUri")
    def image_uri(self) -> builtins.str:
        '''The complete URI of the Docker image for ECS task definitions.

        Format: ``<account-id>.dkr.ecr.<region>.amazonaws.com/<repository-name>:latest``
        '''
        return typing.cast(builtins.str, jsii.get(self, "imageUri"))

    @builtins.property
    @jsii.member(jsii_name="repository")
    def repository(self) -> "_aws_cdk_aws_ecr_ceddda9d.IRepository":
        '''The ECR repository containing the backup Docker image.'''
        return typing.cast("_aws_cdk_aws_ecr_ceddda9d.IRepository", jsii.get(self, "repository"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aurora-native-backup.AuroraBackupRepositoryProps",
    jsii_struct_bases=[],
    name_mapping={"repository_name": "repositoryName"},
)
class AuroraBackupRepositoryProps:
    def __init__(
        self,
        *,
        repository_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Configuration properties for the Aurora backup Docker image.

        :param repository_name: The name of the ECR repository to create. If not provided, CDK will generate a unique name based on the stack and construct ID. Default: CDK-generated name
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20b26c75c4d3f8281996c02787cc9c7abc8140d4c8923be420e4544d8bbd0c83)
            check_type(argname="argument repository_name", value=repository_name, expected_type=type_hints["repository_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if repository_name is not None:
            self._values["repository_name"] = repository_name

    @builtins.property
    def repository_name(self) -> typing.Optional[builtins.str]:
        '''The name of the ECR repository to create.

        If not provided, CDK will generate a unique name based on the stack and construct ID.

        :default: CDK-generated name
        '''
        result = self._values.get("repository_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuroraBackupRepositoryProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AuroraNativeBackupService(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@renovosolutions/cdk-library-aurora-native-backup.AuroraNativeBackupService",
):
    '''A construct for Aurora PostgreSQL native backup service.

    Creates a scheduled ECS Fargate service that performs PostgreSQL backups using ``pg_dump``.
    Backups are written to EFS and then copied to S3. They are removed from EFS after the
    configured ``retentionDays``.
    The S3 bucket for backups can be provided or will be created automatically.

    Example::

        const backupService = new AuroraNativeBackupService(this, 'BackupService', {
          cluster: dbCluster,
          vpc: vpc,
          backupBucketName: 'my-aurora-backups',
          ecrRepository: backupRepository.repository,
          connection: {
            username: 'backup_user',
            databaseNames: ['production', 'analytics', 'reporting'],
            passwordSecret: backupUserSecret,
          },
        });
    '''

    def __init__(
        self,
        scope: "_constructs_77d1e7e8.Construct",
        id: builtins.str,
        *,
        backup_bucket_name: builtins.str,
        cluster: '_IDatabaseCluster_IConnectable',
        connection: typing.Union["AuroraBackupConnectionProps", typing.Dict[builtins.str, typing.Any]],
        ecr_repository: "_aws_cdk_aws_ecr_ceddda9d.IRepository",
        vpc: "_aws_cdk_aws_ec2_ceddda9d.IVpc",
        backup_schedule: typing.Optional["_aws_cdk_aws_scheduler_ceddda9d.ScheduleExpression"] = None,
        cpu: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        retention_days: typing.Optional[jsii.Number] = None,
        schedule_time_window: typing.Optional["_aws_cdk_aws_scheduler_ceddda9d.TimeWindow"] = None,
        subnet_selection: typing.Optional[typing.Union["_aws_cdk_aws_ec2_ceddda9d.SubnetSelection", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''The constructor for the ``AuroraNativeBackupService``.

        This creates a scheduled ECS Fargate service that performs PostgreSQL backups using ``pg_dump``.
        It also creates the ECS cluster, task definition, IAM roles, EFS file system, and S3 bucket for backup storage.

        :param scope: The scope in which to create this Construct. Normally this is a stack.
        :param id: The Construct ID of the backup service.
        :param backup_bucket_name: Name for the S3 backup bucket that will be created by the construct. The bucket will be configured with appropriate settings for backup storage.
        :param cluster: The Aurora PostgreSQL database cluster to backup. Must implement IConnectable for security group configuration.
        :param connection: Database connection configuration.
        :param ecr_repository: ECR repository containing the backup Docker image. The image will be pulled using the imageUri from the ``AuroraBackupRepository`` construct.
        :param vpc: The VPC where the backup service will run.
        :param backup_schedule: Backup schedule using EventBridge Scheduler ScheduleExpression. Use scheduler.ScheduleExpression.cron() or scheduler.ScheduleExpression.rate() to define the schedule. Default: scheduler.ScheduleExpression.cron({ minute: '0', hour: '5' }) - Daily at 5:00 AM UTC
        :param cpu: Fargate task CPU units. Default: 256
        :param memory_limit_mib: Fargate task memory in MB. Default: 512
        :param retention_days: Backup retention period in days. Default: 7
        :param schedule_time_window: The time window during which the scheduled task is allowed to be invoked. This is passed to the EventBridge Scheduler ``Schedule`` as ``timeWindow``. Default: scheduler.TimeWindow.flexible(Duration.minutes(60))
        :param subnet_selection: Subnet selection for the backup task. Default: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS } - Uses private subnets with egress
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61ad4a9cff6ed285be0026a400d5d8ea816bf67626ef5a3dd6ec6ba53165fb21)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = AuroraNativeBackupServiceProps(
            backup_bucket_name=backup_bucket_name,
            cluster=cluster,
            connection=connection,
            ecr_repository=ecr_repository,
            vpc=vpc,
            backup_schedule=backup_schedule,
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            retention_days=retention_days,
            schedule_time_window=schedule_time_window,
            subnet_selection=subnet_selection,
        )

        jsii.create(self.__class__, self, [scope, id, props])

    @builtins.property
    @jsii.member(jsii_name="accessPoint")
    def access_point(self) -> "_aws_cdk_aws_efs_ceddda9d.IAccessPoint":
        '''The EFS access point for backup storage.'''
        return typing.cast("_aws_cdk_aws_efs_ceddda9d.IAccessPoint", jsii.get(self, "accessPoint"))

    @builtins.property
    @jsii.member(jsii_name="backupBucket")
    def backup_bucket(self) -> "_aws_cdk_aws_s3_ceddda9d.Bucket":
        '''The S3 bucket for backup storage.'''
        return typing.cast("_aws_cdk_aws_s3_ceddda9d.Bucket", jsii.get(self, "backupBucket"))

    @builtins.property
    @jsii.member(jsii_name="backupSecurityGroup")
    def backup_security_group(self) -> "_aws_cdk_aws_ec2_ceddda9d.SecurityGroup":
        '''The security group for the backup service.'''
        return typing.cast("_aws_cdk_aws_ec2_ceddda9d.SecurityGroup", jsii.get(self, "backupSecurityGroup"))

    @builtins.property
    @jsii.member(jsii_name="ecsCluster")
    def ecs_cluster(self) -> "_aws_cdk_aws_ecs_ceddda9d.Cluster":
        '''The ECS cluster running the backup service.'''
        return typing.cast("_aws_cdk_aws_ecs_ceddda9d.Cluster", jsii.get(self, "ecsCluster"))

    @builtins.property
    @jsii.member(jsii_name="executionRole")
    def execution_role(self) -> "_aws_cdk_aws_iam_ceddda9d.Role":
        '''The IAM execution role for ECS tasks.'''
        return typing.cast("_aws_cdk_aws_iam_ceddda9d.Role", jsii.get(self, "executionRole"))

    @builtins.property
    @jsii.member(jsii_name="fileSystem")
    def file_system(self) -> "_aws_cdk_aws_efs_ceddda9d.IFileSystem":
        '''The EFS file system for backup storage.'''
        return typing.cast("_aws_cdk_aws_efs_ceddda9d.IFileSystem", jsii.get(self, "fileSystem"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "_aws_cdk_aws_scheduler_ceddda9d.Schedule":
        '''The EventBridge schedule that triggers the backup task.'''
        return typing.cast("_aws_cdk_aws_scheduler_ceddda9d.Schedule", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="schedulerRole")
    def scheduler_role(self) -> "_aws_cdk_aws_iam_ceddda9d.Role":
        '''The IAM role for the EventBridge Scheduler.'''
        return typing.cast("_aws_cdk_aws_iam_ceddda9d.Role", jsii.get(self, "schedulerRole"))

    @builtins.property
    @jsii.member(jsii_name="taskDefinition")
    def task_definition(self) -> "_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition":
        '''The ECS task definition for the backup container.'''
        return typing.cast("_aws_cdk_aws_ecs_ceddda9d.FargateTaskDefinition", jsii.get(self, "taskDefinition"))

    @builtins.property
    @jsii.member(jsii_name="taskRole")
    def task_role(self) -> "_aws_cdk_aws_iam_ceddda9d.Role":
        '''The IAM role for backup tasks.'''
        return typing.cast("_aws_cdk_aws_iam_ceddda9d.Role", jsii.get(self, "taskRole"))


@jsii.data_type(
    jsii_type="@renovosolutions/cdk-library-aurora-native-backup.AuroraNativeBackupServiceProps",
    jsii_struct_bases=[],
    name_mapping={
        "backup_bucket_name": "backupBucketName",
        "cluster": "cluster",
        "connection": "connection",
        "ecr_repository": "ecrRepository",
        "vpc": "vpc",
        "backup_schedule": "backupSchedule",
        "cpu": "cpu",
        "memory_limit_mib": "memoryLimitMiB",
        "retention_days": "retentionDays",
        "schedule_time_window": "scheduleTimeWindow",
        "subnet_selection": "subnetSelection",
    },
)
class AuroraNativeBackupServiceProps:
    def __init__(
        self,
        *,
        backup_bucket_name: builtins.str,
        cluster: '_IDatabaseCluster_IConnectable',
        connection: typing.Union["AuroraBackupConnectionProps", typing.Dict[builtins.str, typing.Any]],
        ecr_repository: "_aws_cdk_aws_ecr_ceddda9d.IRepository",
        vpc: "_aws_cdk_aws_ec2_ceddda9d.IVpc",
        backup_schedule: typing.Optional["_aws_cdk_aws_scheduler_ceddda9d.ScheduleExpression"] = None,
        cpu: typing.Optional[jsii.Number] = None,
        memory_limit_mib: typing.Optional[jsii.Number] = None,
        retention_days: typing.Optional[jsii.Number] = None,
        schedule_time_window: typing.Optional["_aws_cdk_aws_scheduler_ceddda9d.TimeWindow"] = None,
        subnet_selection: typing.Optional[typing.Union["_aws_cdk_aws_ec2_ceddda9d.SubnetSelection", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''Infrastructure configuration properties for Aurora PostgreSQL native backup service.

        :param backup_bucket_name: Name for the S3 backup bucket that will be created by the construct. The bucket will be configured with appropriate settings for backup storage.
        :param cluster: The Aurora PostgreSQL database cluster to backup. Must implement IConnectable for security group configuration.
        :param connection: Database connection configuration.
        :param ecr_repository: ECR repository containing the backup Docker image. The image will be pulled using the imageUri from the ``AuroraBackupRepository`` construct.
        :param vpc: The VPC where the backup service will run.
        :param backup_schedule: Backup schedule using EventBridge Scheduler ScheduleExpression. Use scheduler.ScheduleExpression.cron() or scheduler.ScheduleExpression.rate() to define the schedule. Default: scheduler.ScheduleExpression.cron({ minute: '0', hour: '5' }) - Daily at 5:00 AM UTC
        :param cpu: Fargate task CPU units. Default: 256
        :param memory_limit_mib: Fargate task memory in MB. Default: 512
        :param retention_days: Backup retention period in days. Default: 7
        :param schedule_time_window: The time window during which the scheduled task is allowed to be invoked. This is passed to the EventBridge Scheduler ``Schedule`` as ``timeWindow``. Default: scheduler.TimeWindow.flexible(Duration.minutes(60))
        :param subnet_selection: Subnet selection for the backup task. Default: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS } - Uses private subnets with egress
        '''
        if isinstance(connection, dict):
            connection = AuroraBackupConnectionProps(**connection)
        if isinstance(subnet_selection, dict):
            subnet_selection = _aws_cdk_aws_ec2_ceddda9d.SubnetSelection(**subnet_selection)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2752808b26b09c0f9f05339b6e66a7d79d9f0141cf126126846e5b7b257763a)
            check_type(argname="argument backup_bucket_name", value=backup_bucket_name, expected_type=type_hints["backup_bucket_name"])
            check_type(argname="argument cluster", value=cluster, expected_type=type_hints["cluster"])
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument ecr_repository", value=ecr_repository, expected_type=type_hints["ecr_repository"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument backup_schedule", value=backup_schedule, expected_type=type_hints["backup_schedule"])
            check_type(argname="argument cpu", value=cpu, expected_type=type_hints["cpu"])
            check_type(argname="argument memory_limit_mib", value=memory_limit_mib, expected_type=type_hints["memory_limit_mib"])
            check_type(argname="argument retention_days", value=retention_days, expected_type=type_hints["retention_days"])
            check_type(argname="argument schedule_time_window", value=schedule_time_window, expected_type=type_hints["schedule_time_window"])
            check_type(argname="argument subnet_selection", value=subnet_selection, expected_type=type_hints["subnet_selection"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "backup_bucket_name": backup_bucket_name,
            "cluster": cluster,
            "connection": connection,
            "ecr_repository": ecr_repository,
            "vpc": vpc,
        }
        if backup_schedule is not None:
            self._values["backup_schedule"] = backup_schedule
        if cpu is not None:
            self._values["cpu"] = cpu
        if memory_limit_mib is not None:
            self._values["memory_limit_mib"] = memory_limit_mib
        if retention_days is not None:
            self._values["retention_days"] = retention_days
        if schedule_time_window is not None:
            self._values["schedule_time_window"] = schedule_time_window
        if subnet_selection is not None:
            self._values["subnet_selection"] = subnet_selection

    @builtins.property
    def backup_bucket_name(self) -> builtins.str:
        '''Name for the S3 backup bucket that will be created by the construct.

        The bucket will be configured with appropriate settings for backup storage.
        '''
        result = self._values.get("backup_bucket_name")
        assert result is not None, "Required property 'backup_bucket_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cluster(self) -> '_IDatabaseCluster_IConnectable':
        '''The Aurora PostgreSQL database cluster to backup.

        Must implement IConnectable for security group configuration.
        '''
        result = self._values.get("cluster")
        assert result is not None, "Required property 'cluster' is missing"
        return typing.cast('_IDatabaseCluster_IConnectable', result)

    @builtins.property
    def connection(self) -> "AuroraBackupConnectionProps":
        '''Database connection configuration.'''
        result = self._values.get("connection")
        assert result is not None, "Required property 'connection' is missing"
        return typing.cast("AuroraBackupConnectionProps", result)

    @builtins.property
    def ecr_repository(self) -> "_aws_cdk_aws_ecr_ceddda9d.IRepository":
        '''ECR repository containing the backup Docker image.

        The image will be pulled using the imageUri from the ``AuroraBackupRepository`` construct.
        '''
        result = self._values.get("ecr_repository")
        assert result is not None, "Required property 'ecr_repository' is missing"
        return typing.cast("_aws_cdk_aws_ecr_ceddda9d.IRepository", result)

    @builtins.property
    def vpc(self) -> "_aws_cdk_aws_ec2_ceddda9d.IVpc":
        '''The VPC where the backup service will run.'''
        result = self._values.get("vpc")
        assert result is not None, "Required property 'vpc' is missing"
        return typing.cast("_aws_cdk_aws_ec2_ceddda9d.IVpc", result)

    @builtins.property
    def backup_schedule(
        self,
    ) -> typing.Optional["_aws_cdk_aws_scheduler_ceddda9d.ScheduleExpression"]:
        '''Backup schedule using EventBridge Scheduler ScheduleExpression.

        Use scheduler.ScheduleExpression.cron() or scheduler.ScheduleExpression.rate() to define the schedule.

        :default: scheduler.ScheduleExpression.cron({ minute: '0', hour: '5' }) - Daily at 5:00 AM UTC

        :see: https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-cron-expressions.html

        Example::

            // Weekly on Sundays at 2 AM UTC
            backupSchedule: scheduler.ScheduleExpression.cron({ minute: '0', hour: '2', weekDay: 'SUN' })
        '''
        result = self._values.get("backup_schedule")
        return typing.cast(typing.Optional["_aws_cdk_aws_scheduler_ceddda9d.ScheduleExpression"], result)

    @builtins.property
    def cpu(self) -> typing.Optional[jsii.Number]:
        '''Fargate task CPU units.

        :default: 256
        '''
        result = self._values.get("cpu")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_limit_mib(self) -> typing.Optional[jsii.Number]:
        '''Fargate task memory in MB.

        :default: 512
        '''
        result = self._values.get("memory_limit_mib")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def retention_days(self) -> typing.Optional[jsii.Number]:
        '''Backup retention period in days.

        :default: 7
        '''
        result = self._values.get("retention_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def schedule_time_window(
        self,
    ) -> typing.Optional["_aws_cdk_aws_scheduler_ceddda9d.TimeWindow"]:
        '''The time window during which the scheduled task is allowed to be invoked.

        This is passed to the EventBridge Scheduler ``Schedule`` as ``timeWindow``.

        :default: scheduler.TimeWindow.flexible(Duration.minutes(60))
        '''
        result = self._values.get("schedule_time_window")
        return typing.cast(typing.Optional["_aws_cdk_aws_scheduler_ceddda9d.TimeWindow"], result)

    @builtins.property
    def subnet_selection(
        self,
    ) -> typing.Optional["_aws_cdk_aws_ec2_ceddda9d.SubnetSelection"]:
        '''Subnet selection for the backup task.

        :default: { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS } - Uses private subnets with egress
        '''
        result = self._values.get("subnet_selection")
        return typing.cast(typing.Optional["_aws_cdk_aws_ec2_ceddda9d.SubnetSelection"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AuroraNativeBackupServiceProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AuroraBackupConnectionProps",
    "AuroraBackupRepository",
    "AuroraBackupRepositoryProps",
    "AuroraNativeBackupService",
    "AuroraNativeBackupServiceProps",
]

publication.publish()

def _typecheckingstub__373be5d587e3914f8f2c064a490876c36c34094185d72d447d8942426a1489bd(
    *,
    password_secret: _aws_cdk_aws_secretsmanager_ceddda9d.ISecret,
    username: builtins.str,
    database_names: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cadd1c8e90a4309ad8370d70b5c9f6c73101a7e430d62e74d6087d71baca8b4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    repository_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25622354894e991f1a249e2cb7693232d5b2b058af8ccb5277b31f87eec94bcb(
    grantee: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4045bb29c2d773d57ae664aaf513384b2e67dfbed4ca98c1afdc621bb87ea5ba(
    grantee: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04796329b3961abe09d968683c47dbc71e660bee40c2c0f4ade11e8da9ea6949(
    grantee: _aws_cdk_aws_iam_ceddda9d.IPrincipal,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20b26c75c4d3f8281996c02787cc9c7abc8140d4c8923be420e4544d8bbd0c83(
    *,
    repository_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61ad4a9cff6ed285be0026a400d5d8ea816bf67626ef5a3dd6ec6ba53165fb21(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    backup_bucket_name: builtins.str,
    cluster: '_IDatabaseCluster_IConnectable',
    connection: typing.Union[AuroraBackupConnectionProps, typing.Dict[builtins.str, typing.Any]],
    ecr_repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    backup_schedule: typing.Optional[_aws_cdk_aws_scheduler_ceddda9d.ScheduleExpression] = None,
    cpu: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    retention_days: typing.Optional[jsii.Number] = None,
    schedule_time_window: typing.Optional[_aws_cdk_aws_scheduler_ceddda9d.TimeWindow] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2752808b26b09c0f9f05339b6e66a7d79d9f0141cf126126846e5b7b257763a(
    *,
    backup_bucket_name: builtins.str,
    cluster: '_IDatabaseCluster_IConnectable',
    connection: typing.Union[AuroraBackupConnectionProps, typing.Dict[builtins.str, typing.Any]],
    ecr_repository: _aws_cdk_aws_ecr_ceddda9d.IRepository,
    vpc: _aws_cdk_aws_ec2_ceddda9d.IVpc,
    backup_schedule: typing.Optional[_aws_cdk_aws_scheduler_ceddda9d.ScheduleExpression] = None,
    cpu: typing.Optional[jsii.Number] = None,
    memory_limit_mib: typing.Optional[jsii.Number] = None,
    retention_days: typing.Optional[jsii.Number] = None,
    schedule_time_window: typing.Optional[_aws_cdk_aws_scheduler_ceddda9d.TimeWindow] = None,
    subnet_selection: typing.Optional[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

class _IDatabaseCluster_IConnectable(_aws_cdk_aws_rds_ceddda9d.IDatabaseCluster, _aws_cdk_aws_ec2_ceddda9d.IConnectable, typing_extensions.Protocol):
    pass

for cls in [_IDatabaseCluster_IConnectable]:
    typing.cast(typing.Any, cls).__protocol_attrs__ = typing.cast(typing.Any, cls).__protocol_attrs__ - set(['__jsii_proxy_class__', '__jsii_type__'])
