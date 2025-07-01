from storages.backends.s3boto3 import S3Boto3Storage


class SupabasePublicMediaStorage(S3Boto3Storage):
    """Custom storage to handle Supabase public URLs."""
    default_acl = 'public-read'
    file_overwrite = False

    def url(self, name):
        if name.startswith(f"{self.bucket_name}/"):
            name = name[len(f"{self.bucket_name}/"):]

        endpoint = self.endpoint_url.split('//')[-1].split('/')[0]
        return (
            f"https://{endpoint}/storage/v1/object/public/"
            f"{self.bucket_name}/{name}"
        )
