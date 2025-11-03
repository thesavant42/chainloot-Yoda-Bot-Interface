-- Create prompt_templates table
CREATE TABLE "prompt_templates" (
    "id" TEXT NOT NULL DEFAULT gen_random_uuid(),
    "name" TEXT NOT NULL,
    "toml_content" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "prompt_templates_pkey" PRIMARY KEY ("id")
);

-- Create index for name lookups
CREATE INDEX "prompt_templates_name_idx" ON "prompt_templates"("name");