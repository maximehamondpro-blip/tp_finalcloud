module "source_bucket" {
  source      = "./modules/s3"
  bucket_name = var.bucket_source_name
}
module "dest_bucket" {
  source      = "./modules/s3"
  bucket_name = var.bucket_dest_name
}
module "image_processor_lambda" {
  source            = "./modules/lambda"
  function_name     = "image_processor_pdf_converter"
  source_bucket_id  = module.source_bucket.bucket_id
  source_bucket_arn = module.source_bucket.bucket_arn
  dest_bucket_arn   = module.dest_bucket.bucket_arn
  lambda_zip_path   = "../src/lambda_function.zip"
}
