import json
import os
import platform
import requests
import shutil
import stat
import time
import unittest
from unittest.mock import patch
from click.testing import CliRunner
from contextlib import redirect_stdout
from nomad_media_cli.cli import cli
from nomad_media_cli.helpers.get_content_definition_id import get_content_definition_id

class TestAssetBase(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        cls.runner = CliRunner()

        with open("nomad_media_cli/tests/test-config.json", "r") as file:
            test_config = json.load(file)
            cls.test_dir_id = test_config["testDirId"]
            
        test_dir_contents = get_total_asset_list(cls, cls.test_dir_id)
        
        config_path_result = cls.runner.invoke(cli, ["list-config-path"])
        if config_path_result.exit_code != 0:
            raise Exception(f"Need to run `nomad-media-cli init` before running tests")
        
        config_path = json.loads(config_path_result.output.strip())

        with open(config_path["path"], "r") as file:
            config = json.load(file)
            cls.config = config
            cls.config_path = config_path["path"]

        if test_dir_contents:
            test_dir_files = [item for item in test_dir_contents if item["assetTypeDisplay"] == "File" and item["mediaTypeDisplay"] == "Video"]
        else:
            test_dir_files = []

        if config["apiType"] == "admin":
            cls.existing_asset = False
            result = cls.runner.invoke(cli, [
                "upload-assets", 
                "--source", "./nomad_media_cli/tests/test_files/vid1.mp4",
                "--id", cls.test_dir_id
            ])
           
            if result.exit_code != 0:
               raise Exception(f"Failed to upload asset: {result.output}")
           
            cls.asset_id = json.loads(result.output)[0]["id"]           

        elif config["apiType"] == "portal" and len(test_dir_files) == 0:
           raise unittest.SkipTest("No assets found in test directory")
        else:
            cls.existing_asset = True
            cls.asset_id = test_dir_files[0]["id"]
            
    @classmethod
    def tearDownClass(cls):
        if not cls.existing_asset and cls.config["apiType"] == "admin":
            result = cls.runner.invoke(cli, [
                "delete-asset", 
                "--id", cls.asset_id
            ])

            if result.exit_code != 0:
                raise Exception(f"Failed to delete asset: {result.output}")

            print(f"Deleted asset with id: {cls.asset_id}")

class TestAssetArchive(TestAssetBase):
    """Tests for archiving assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_archive_asset_by_id(self):
        """Test asset is archived successfully"""        

        result = self.runner.invoke(cli, [
            "archive-asset", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_archive_asset_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "archive-asset", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            
    def test_archive_asset_by_url(self):
        """Test asset is archived successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "archive-asset", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_archive_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "archive-asset", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            
    def test_archive_asset_by_object_key(self):
        """Test asset is archived successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "archive-asset", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_archive_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "archive-asset", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_archive_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "archive-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestBuildMedia(TestAssetBase):
    """Tests for building media"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()        

        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not admin")
        

    def test_build_media_by_id(self):
        """Test media is built successfully"""
        result = self.runner.invoke(cli, [
            "build-media", 
            "--source-ids", f'{{ "sourceAssetId": "{self.asset_id}" }}',
            "--destination-folder-id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_build_media_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "build-media", 
            "--source-ids", f'{{ "sourceAssetId": "invalid-id" }}',
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_build_media_by_url(self):
        """Test media is built successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "build-media", 
            "--source-urls", f'{{ "url": "{url}" }}',
            "--destination-folder-id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)

    def test_build_media_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "build-media", 
            "--source-urls", f'{{ "url": "invalid-url" }}',
            "--destination-folder-id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_build_media_by_object_key(self):
        """Test media is built successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "build-media", 
            "--source-object-keys", f'{{ "object_key": "{object_key}" }}',
            "--destination-folder-id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)

    def test_build_media_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details",
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "build-media",
            "--source-object-keys", f'[{{ "object_key": "{object_key}" }}]',
            "--destination-folder-id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_build_media_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "build-media",
            "--source-object-keys", f'[{{ "object_key": "invalid-object-key" }}]',
            "--destination-folder-id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_build_media_by_id_add_tag_by_name(self):
        """Test media is built successfully with tag"""
        tag_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "tag"
        ])
        
        tag_contents = json.loads(tag_contents.output)
        
        result = self.runner.invoke(cli, [
            "build-media",
            "--source-ids", f'{{ "sourceAssetId": "{self.asset_id}" }}',
            "--destination-folder-id", self.test_dir_id,
            "--tag-names", tag_contents[0]["title"],
            "--tag-names", tag_contents[1]["title"]
        ])
        
        self.assertEqual(result.exit_code, 0)

class TestClipAsset(TestAssetBase):
    """Tests for clipping assets"""
    def test_clip_asset_by_id(self):
        """Test asset is clipped successfully"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_assets = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.test_dir_id
        ])
        
        test_clip_asset = next((item for item in json.loads(parent_assets.output)["items"] if item["name"] == "test_clip.mp4"), None)
        self.assertTrue(test_clip_asset)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", test_clip_asset["id"]
        ])
        
    def test_clip_asset_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", "invalid-id",
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            
    def test_clip_asset_by_url(self):
        """Test asset is clipped successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--url", url,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_assets = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.test_dir_id
        ])
        
        test_clip_asset = next((item for item in json.loads(parent_assets.output)["items"] if item["name"] == "test_clip.mp4"), None)
        self.assertTrue(test_clip_asset)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", test_clip_asset["id"]
        ])
        
    def test_clip_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--url", "invalid-url",
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            
    def test_clip_asset_by_object_key(self):
        """Test asset is clipped successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--object-key", object_key,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_assets = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.test_dir_id
        ])
        
        test_clip_asset = next((item for item in json.loads(parent_assets.output)["items"] if item["name"] == "test_clip.mp4"), None)
        self.assertTrue(test_clip_asset)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", test_clip_asset["id"]
        ])
        
    def test_clip_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--object-key", object_key,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_clip_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--object-key", "invalid-object-key",
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_clip_asset_by_id_add_tag_by_name(self):
        """Test asset is clipped successfully with tag"""
        tag_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "tag"
        ])

        tag_contents = json.loads(tag_contents.output)        

        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--tag-names", tag_contents[0]["title"],
            "--tag-names", tag_contents[1]["title"]
        ])

        self.assertEqual(result.exit_code, 0)

        parent_assets = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.test_dir_id
        ])

        test_clip_asset = next((item for item in json.loads(parent_assets.output)["items"] if "test_clip" in item["name"]), None)
        self.assertIsNotNone(test_clip_asset)

        clip_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", test_clip_asset["id"]
        ])

        clip_info = json.loads(clip_info_result.output)
        self.assertTrue(any(tag_contents[0]["title"] in tag["title"] for tag in clip_info["tags"]))
        self.assertTrue(any(tag_contents[1]["title"] in tag["title"] for tag in clip_info["tags"]))

        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", test_clip_asset["id"]
        ])

    def test_clip_asset_by_id_add_tag_by_name_invalid(self):
        """Test invalid tag name returns an error"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--tag-names", "invalid-tag-name"
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_clip_asset_by_id_add_tag_by_ids(self):
        """Test asset is clipped successfully with tag"""
        tag_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "tag"
        ])

        tag_contents = json.loads(tag_contents.output)
        
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--tag_ids", tag_contents[0]["id"],
            "--tag_ids", tag_contents[1]["id"]
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_assets = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.test_dir_id
        ])
        
        test_clip_asset = next((item for item in json.loads(parent_assets.output)["items"] if "test_clip" in item["name"]), None)
        self.assertIsNotNone(test_clip_asset)
        
        clip_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", test_clip_asset["id"]
        ])
        
        clip_info = json.loads(clip_info_result.output)
        self.assertTrue(any(tag_contents[0]["id"] == tag["id"] for tag in clip_info["tags"]))
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", test_clip_asset["id"]
        ])

    def test_clip_asset_by_id_add_tag_by_id_invalid(self):
        """Test invalid tag ID returns an error"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--tag_ids", "invalid-tag-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_clip_asset_by_id_add_collection_by_name(self):
        """Test asset is clipped successfully with collection"""
        collection_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "collection"
        ])
        
        collection_contents = json.loads(collection_contents.output)

        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--collection-names", collection_contents[0]["title"],
            "--collection-names", collection_contents[1]["title"]
        ])

        self.assertEqual(result.exit_code, 0)

        parent_assets = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.test_dir_id
        ])

        test_clip_asset = next((item for item in json.loads(parent_assets.output)["items"] if "test_clip" in item["name"]), None)
        self.assertIsNotNone(test_clip_asset)

        clip_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", test_clip_asset["id"]
        ])

        clip_info = json.loads(clip_info_result.output)
        self.assertTrue(any(collection_contents[0]["title"] in collection["description"] for collection in clip_info["collections"]))
        self.assertTrue(any(collection_contents[1]["title"] in collection["description"] for collection in clip_info["collections"]))

        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", test_clip_asset["id"]
        ])
        
    def test_clip_asset_by_id_add_collection_by_name_invalid(self):
        """Test invalid collection name returns an error"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--collection-names", "invalid-collection-name"
        ])

        self.assertNotEqual(result.exit_code, 0)
        
    def test_clip_asset_by_id_add_collection_by_ids(self):
        """Test asset is clipped successfully with collection"""
        collection_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "collection"
        ])

        collection_contents = json.loads(collection_contents.output)
        
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--collection_ids", collection_contents[0]["id"],
            "--collection_ids", collection_contents[1]["id"]
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_assets = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.test_dir_id
        ])
        
        test_clip_asset = next((item for item in json.loads(parent_assets.output)["items"] if "test_clip" in item["name"]), None)
        self.assertIsNotNone(test_clip_asset)
        
        clip_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", test_clip_asset["id"]
        ])
        
        clip_info = json.loads(clip_info_result.output)
        self.assertTrue(any(collection_contents[0]["id"] == collection["id"] for collection in clip_info["collections"]))
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", test_clip_asset["id"]
        ])
        
    def test_clip_asset_by_id_add_collection_by_id_invalid(self):
        """Test invalid collection ID returns an error"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--collection_ids", "invalid-collection-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_clip_asset_by_id_add_related_content_by_ids(self):
        """Test asset is clipped successfully with related content"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--related-content_ids", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_assets = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.test_dir_id
        ])
        
        test_clip_asset = next((item for item in json.loads(parent_assets.output)["items"] if "test_clip" in item["name"]), None)
        self.assertIsNotNone(test_clip_asset)
        
        clip_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", test_clip_asset["id"]
        ])
        
        clip_info = json.loads(clip_info_result.output)
        self.assertTrue(any(self.asset_id == related_content["id"] for related_content in clip_info["relatedContent"]))
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", test_clip_asset["id"]
        ])
        
    def test_clip_asset_by_id_add_related_content_by_id_invalid(self):
        """Test invalid related content ID returns an error"""
        result = self.runner.invoke(cli, [
            "clip-asset", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
            "--end-time-code", "00:00:05;00",
            "--title", "test_clip",
            "--output-folder-id", self.test_dir_id,
            "--related-content_ids", "invalid-related-content-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestCopyAsset(TestAssetBase):
    """Tests for copying assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")
        
        create_folder_result = cls.runner.invoke(cli, [
            "create-folder-asset",
            "--parent-id", cls.test_dir_id,
            "--display-name", "test_copy_folder"
        ])
        
        test_dir = create_folder_result.output.strip()
        cls.copy_dir_id = json.loads(test_dir)["id"]
        
        asset_details_result = cls.runner.invoke(cli, [
            "get-asset-details",
            "--id", cls.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        cls.asset_display_name = asset_details["properties"]["displayName"]

    @classmethod
    def tearDownClass(cls):
        result = cls.runner.invoke(cli, [
            "delete-asset", 
            "--id", cls.copy_dir_id
        ])
        
        if result.exit_code != 0:
            raise Exception(f"Failed to delete asset: {result.output}")
        
        print(f"Deleted asset with id: {cls.copy_dir_id}")

    def test_copy_asset_by_id(self):
        """Test asset is copied successfully"""
        result = self.runner.invoke(cli, [
            "copy-asset", 
            "--id", self.asset_id,
            "--destination-folder-id", self.copy_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)

        copy_dir_details = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.copy_dir_id
        ])
        
        copy_asset = next((item for item in json.loads(copy_dir_details.output)["items"] if item["name"] == self.asset_display_name), None)
        self.assertTrue(copy_asset)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", copy_asset["id"]
        ])
        
    def test_copy_asset_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "copy-asset", 
            "--id", "invalid-id",
            "--destination-folder-id", self.copy_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            
    def test_copy_asset_by_url(self):
        """Test asset is copied successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "copy-asset", 
            "--url", url,
            "--destination-folder-id", self.copy_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)

        copy_dir_details = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.copy_dir_id
        ])
        
        copy_asset = next((item for item in json.loads(copy_dir_details.output)["items"] if item["name"] == self.asset_display_name), None)
        self.assertTrue(copy_asset)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", copy_asset["id"]
        ])
        
    def test_copy_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "copy-asset", 
            "--url", "invalid-url",
            "--destination-folder-id", self.copy_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            
    def test_copy_asset_by_object_key(self):
        """Test asset is copied successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "copy-asset", 
            "--object-key", object_key,
            "--destination-folder-id", self.copy_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        copy_dir_details = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.copy_dir_id
        ])
        
        copy_asset = next((item for item in json.loads(copy_dir_details.output)["items"] if item["name"] == self.asset_display_name), None)
        self.assertTrue(copy_asset)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", copy_asset["id"]
        ])
        
    def test_copy_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "copy-asset", 
            "--object-key", object_key,
            "--destination-folder-id", self.copy_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_copy_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "copy-asset", 
            "--object-key", "invalid-object-key",
            "--destination-folder-id", self.copy_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestCreateAnnotation(TestAssetBase):
    """Tests for creating annotations"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")

    def test_create_annotation_by_id(self):
        """Test annotation is created successfully"""
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotation_results = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotation_results.output)
        self.assertTrue(annotations)
        
        self.runner.invoke(cli, [
            "delete-annotation", 
            "--id", annotations[0]["id"]
        ])
        
    def test_create_annotation_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--id", "invalid-id",
            "--start-time-code", "00:00:00;00",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_annotation_by_url(self):
        """Test annotation is created successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--url", url,
            "--start-time-code", "00:00:00;00",
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotation_results = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotation_results.output)
        self.assertTrue(annotations)
        
        self.runner.invoke(cli, [
            "delete-annotation", 
            "--id", annotations[0]["id"]
        ])
        
    def test_create_annotation_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--url", "invalid-url",
            "--start-time-code", "00:00:00;00",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_annotation_by_object_key(self):
        """Test annotation is created successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--object-key", object_key,
            "--start-time-code", "00:00:00;00",
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotation_results = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotation_results.output)
        self.assertTrue(annotations)
        
        self.runner.invoke(cli, [
            "delete-annotation", 
            "--id", annotations[0]["id"]
        ])
        
    def test_create_annotation_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--object-key", object_key,
            "--start-time-code", "00:00:00;00",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_annotation_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--object-key", "invalid-object-key",
            "--start-time-code", "00:00:00;00",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_annotation_add_metadata(self):
        """Test annotation is created successfully with metadata"""
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;05",
            "--title", "test_annotation",
            "--summary", "test_annotation_summary",
            "--description", "test_annotation_description"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotation_results = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotation_results.output)
        self.assertTrue(annotations)
    
        annotation = next((annotation for annotation in annotations if annotation["startTimeCode"] == "00:00:00;05"), None)
        self.assertTrue(annotation)
        
        self.assertEqual(annotation["properties"]["title"], "test_annotation")
        self.assertEqual(annotation["properties"]["summary"], "test_annotation_summary")
        self.assertEqual(annotation["properties"]["description"], "test_annotation_description")
        
        self.runner.invoke(cli, [
            "delete-annotation",
            "--id", annotation["id"]
        ])
        
class TestCreateAssetAdBreak(TestAssetBase):
    """Tests for creating asset ad breaks"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_create_asset_ad_break_by_id(self):
        """Test asset ad break is created successfully"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_breaks = json.loads(ad_break_results.output)
        self.assertTrue(ad_breaks)

        ad_breaks = [ad_break for ad_break in ad_breaks if ad_break["id"] != self.asset_id]
        
        self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", ad_breaks[0]["id"]
        ])
        
    def test_create_asset_ad_break_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", "invalid-id",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_asset_ad_break_by_url(self):
        """Test asset ad break is created successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--url", url,
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_breaks = json.loads(ad_break_results.output)
        self.assertTrue(ad_breaks)

        ad_breaks = [ad_break for ad_break in ad_breaks if ad_break["id"] != self.asset_id]
        
        self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", ad_breaks[0]["id"]
        ])
        
    def test_create_asset_ad_break_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--url", "invalid-url",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_asset_ad_break_by_object_key(self):
        """Test asset ad break is created successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--object-key", object_key,
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_breaks = json.loads(ad_break_results.output)
        self.assertTrue(ad_breaks)
        
        ad_breaks = [ad_break for ad_break in ad_breaks if ad_break["id"] != self.asset_id]
        
        self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", ad_breaks[0]["id"]
        ])
        
    def test_create_asset_ad_break_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--object-key", object_key,
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_asset_ad_break_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--object-key", "invalid-object-key",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_asset_ad_break_by_id_add_tag_by_name(self):
        """Test asset ad break is created successfully with tag"""
        tag_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "tag"
        ])

        tag_contents = json.loads(tag_contents.output)        

        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
            "--tag-names", tag_contents[0]["title"],
            "--tag-names", tag_contents[1]["title"]
        ])

        self.assertEqual(result.exit_code, 0)

        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])

        ad_breaks = json.loads(ad_break_results.output)
        self.assertTrue(ad_breaks)

        ad_breaks = [ad_break for ad_break in ad_breaks if ad_break["id"] != self.asset_id]

        self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", ad_breaks[0]["id"]
        ])
        
    def test_create_asset_ad_break_by_id_add_tag_by_name_invalid(self):
        """Test invalid tag name returns an error"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
            "--tag-names", "invalid-tag-name"
        ])

        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_asset_ad_break_by_id_add_tag_by_ids(self):
        """Test asset ad break is created successfully with tag"""
        tag_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "tag"
        ])

        tag_contents = json.loads(tag_contents.output)
        
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
            "--tag_ids", tag_contents[0]["id"],
            "--tag_ids", tag_contents[1]["id"]
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_breaks = json.loads(ad_break_results.output)
        self.assertTrue(ad_breaks)
        
        ad_breaks = [ad_break for ad_break in ad_breaks if ad_break["id"] != self.asset_id]
        
        self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", ad_breaks[0]["id"]
        ])
        
    def test_create_asset_ad_break_by_id_add_tag_by_id_invalid(self):
        """Test invalid tag ID returns an error"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
            "--tag_ids", "invalid-tag-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_asset_ad_break_by_id_add_label_by_name(self):
        """Test asset ad break is created successfully with label"""
        label_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "label"
        ])

        label_contents = json.loads(label_contents.output)        

        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
            "--label-names", label_contents[0]["title"],
            "--label-names", label_contents[1]["title"]
        ])

        self.assertEqual(result.exit_code, 0)

        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])

        ad_breaks = json.loads(ad_break_results.output)
        self.assertTrue(ad_breaks)

        ad_breaks = [ad_break for ad_break in ad_breaks if ad_break["id"] != self.asset_id]

        self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", ad_breaks[0]["id"]
        ])
        
    def test_create_asset_ad_break_by_id_add_label_by_name_invalid(self):
        """Test invalid label name returns an error"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
            "--label-names", "invalid-label-name"
        ])

        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_asset_ad_break_by_id_add_label_by_ids(self):
        """Test asset ad break is created successfully with label"""
        label_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "label"
        ])

        label_contents = json.loads(label_contents.output)
        
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
            "--label_ids", label_contents[0]["id"],
            "--label_ids", label_contents[1]["id"]
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_breaks = json.loads(ad_break_results.output)
        self.assertTrue(ad_breaks)
        
        ad_breaks = [ad_break for ad_break in ad_breaks if ad_break["id"] != self.asset_id]
        
        self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", ad_breaks[0]["id"]
        ])
        
    def test_create_asset_ad_break_by_id_add_label_by_id_invalid(self):
        """Test invalid label ID returns an error"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
            "--label_ids", "invalid-label-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestCreateFolderAsset(TestAssetBase):
    """Tests for creating folder assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_create_folder_asset_by_id(self):
        """Test folder asset is created successfully"""
        result = self.runner.invoke(cli, [
            "create-folder-asset", 
            "--parent-id", self.test_dir_id,
            "--display-name", "test_folder"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result_output = json.loads(result.output)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", result_output["id"]
        ])
        
    def test_create_folder_asset_by_id(self):
        """Test invalid parent ID returns an error"""
        result = self.runner.invoke(cli, [
            "create-folder-asset", 
            "--parent-id", "invalid-id",
            "--display-name", "test_folder"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_folder_asset_by_url(self):
        """Test folder asset is created successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]        

        result = self.runner.invoke(cli, [
            "create-folder-asset", 
            "--url", url,
            "--display-name", "test_folder"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result_output = json.loads(result.output)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", result_output["id"]
        ])
        
    def test_create_folder_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "create-folder-asset", 
            "--url", "invalid-url",
            "--display-name", "test_folder"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_folder_asset_by_object_key(self):
        """Test folder asset is created successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-folder-asset", 
            "--object-key", object_key,
            "--display-name", "test_folder"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result_output = json.loads(result.output)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", result_output["id"]
        ])
        
    def test_create_folder_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-folder-asset", 
            "--object-key", object_key,
            "--display-name", "test_folder"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_folder_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "create-folder-asset", 
            "--object-key", "invalid-object-key",
            "--display-name", "test_folder"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestCreatePlaceholderAsset(TestAssetBase):
    """Tests for creating placeholder assets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_create_placeholder_asset_by_id(self):
        """Test placeholder asset is created successfully"""
        result = self.runner.invoke(cli, [
            "create-placeholder-asset", 
            "--parent-id", self.test_dir_id,
            "--asset-name", "test_placeholder.txt"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result_output = json.loads(result.output)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", result_output["id"]
        ])

    def test_create_placeholder_asset_by_id(self):
        """Test invalid parent ID returns an error"""
        result = self.runner.invoke(cli, [
            "create-placeholder-asset", 
            "--parent-id", "invalid-id",
            "--asset-name", "test_placeholder.txt"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_placeholder_invalid_asset_name(self):
        """Test invalid asset name returns an error"""
        result = self.runner.invoke(cli, [
            "create-placeholder-asset", 
            "--parent-id", self.test_dir_id,
            "--asset-name", "test_placeholder"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_create_placeholder_asset_by_url(self):
        """Test placeholder asset is created successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]        

        result = self.runner.invoke(cli, [
            "create-placeholder-asset", 
            "--url", url,
            "--asset-name", "test_placeholder.txt"    
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result_output = json.loads(result.output)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", result_output["id"]
        ])  

    def test_create_placeholder_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "create-placeholder-asset", 
            "--url", "invalid-url",
            "--asset-name", "test_placeholder.txt"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_create_placeholder_asset_by_object_key(self):
        """Test placeholder asset is created successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-placeholder-asset", 
            "--object-key", object_key,
            "--asset-name", "test_placeholder.txt"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result_output = json.loads(result.output)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", result_output["id"]
        ])

    def test_create_placeholder_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "create-placeholder-asset", 
            "--object-key", object_key,
            "--asset-name", "test_placeholder.txt"
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_create_placeholder_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "create-placeholder-asset", 
            "--object-key", "invalid-object-key",
            "--asset-name", "test_placeholder.txt"
        ])

        self.assertNotEqual(result.exit_code, 0)

class TestCreateScreenshotAtTimecode(TestAssetBase):
    """Tests for creating screenshots at timecode"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")
        
    def test_create_screenshot_at_timecode(self):
        """Test screenshot is created successfully"""
        result = self.runner.invoke(cli, [
            "create-screenshot-at-timecode", 
            "--id", self.asset_id,
            "--time-code", "00:00:00;01"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_create_screenshot_at_timecode_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "create-screenshot-at-timecode", 
            "--id", "invalid-id",
            "--time-code", "00:00:00;00"
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_create_screenshot_at_timecode_by_url(self):
        """Test screenshot is created successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]

        result = self.runner.invoke(cli, [
            "create-screenshot-at-timecode", 
            "--url", url,
            "--time-code", "00:00:00;00"
        ])

        self.assertEqual(result.exit_code, 0)
        
    def test_create_screenshot_at_timecode_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "create-screenshot-at-timecode", 
            "--url", "invalid-url",
            "--time-code", "00:00:00;00"
        ])

        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_screenshot_at_timecode_by_object_key(self):
        """Test screenshot is created successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-screenshot-at-timecode", 
            "--object-key", object_key,
            "--time-code", "00:00:00;00"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_create_screenshot_at_timecode_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-screenshot-at-timecode", 
            "--object-key", object_key,
            "--time-code", "00:00:00;00"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_create_screenshot_at_timecode_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "create-screenshot-at-timecode", 
            "--object-key", "invalid-object-key",
            "--time-code", "00:00:00;00"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestDeleteAnnotation(TestAssetBase):
    """Tests for deleting annotations"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")

    def test_delete_annotation(self):
        """Test annotation is deleted successfully"""
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--id", self.asset_id,
            "--start-time-code", "00:00:00;00",
        ])
        
        annotation = json.loads(result.output)
        annotation_id = annotation["id"]    

        result = self.runner.invoke(cli, [
            "delete-annotation", 
            "--id", self.asset_id,
            "--annotation-id", annotation_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        time.sleep(5)

        annotation_results = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotation_results.output)
        self.assertIsNone(next((item for item in annotations if item["id"] == annotation_id), None))
        
    def test_delete_annotation_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "delete-annotation", 
            "--id", "invalid-id",
            "--annotation-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_annotation_invalid_annotation_id(self):
        """Test invalid annotation ID returns an error"""
        result = self.runner.invoke(cli, [
            "delete-annotation",
            "--id", self.asset_id,
            "--annotation-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_annotation_by_url(self):
        """Test annotation is deleted successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--url", url,
            "--start-time-code", "00:00:00;00",
        ])
        
        annotation = json.loads(result.output)
        annotation_id = annotation["id"]
        
        result = self.runner.invoke(cli, [
            "delete-annotation", 
            "--id", self.asset_id,
            "--annotation-id", annotation_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotation_results = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotation_results.output)
        self.assertIsNone(next((item for item in annotations if item["id"] == annotation_id), None))
        
    def test_delete_annotation_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "delete-annotation", 
            "--url", "invalid-url",
            "--annotation-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_annotation_by_object_key(self):
        """Test annotation is deleted successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--object-key", object_key,
            "--start-time-code", "00:00:00;00",
        ])
        
        annotation = json.loads(result.output)
        annotation_id = annotation["id"]
        
        result = self.runner.invoke(cli, [
            "delete-annotation", 
            "--id", self.asset_id,
            "--annotation-id", annotation_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotation_results = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotation_results.output)
        self.assertIsNone(next((item for item in annotations if item["id"] == annotation_id), None))
        
    def test_delete_annotation_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-annotation", 
            "--object-key", object_key,
            "--start-time-code", "00:00:00;00",
        ])
        
        annotation = json.loads(result.output)
        annotation_id = annotation["id"]
        
        result = self.runner.invoke(cli, [
            "delete-annotation", 
            "--id", self.asset_id,
            "--annotation-id", annotation_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_annotation_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "delete-annotation", 
            "--object-key", "invalid-object-key",
            "--annotation-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestDeleteAssetAdBreak(TestAssetBase):
    """Tests for deleting asset ad breaks"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_delete_asset_ad_break(self):
        """Test asset ad break is deleted successfully"""
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", self.asset_id,
        ])
        
        ad_break = json.loads(result.output)
        ad_break_id = ad_break["id"]   

        result = self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", self.asset_id,
            "--ad-break-id", ad_break_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_breaks = json.loads(ad_break_results.output)
        self.assertIsNone(next((item for item in ad_breaks if item["id"] == ad_break_id), None))
        
    def test_delete_asset_ad_break_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", "invalid-id",
            "--ad-break-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_asset_ad_break_by_url(self):
        """Test asset ad break is deleted successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--url", url,
        ])
        
        ad_break = json.loads(result.output)
        ad_break_id = ad_break["id"]
        
        result = self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", self.asset_id,
            "--ad-break-id", ad_break_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_breaks = json.loads(ad_break_results.output)
        self.assertIsNone(next((item for item in ad_breaks if item["id"] == ad_break_id), None))
        
    def test_delete_asset_ad_break_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_asset_ad_break_by_object_key(self):
        """Test asset ad break is deleted successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--object-key", object_key,
        ])
        
        ad_break = json.loads(result.output)
        ad_break_id = ad_break["id"]
        
        result = self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", self.asset_id,
            "--ad-break-id", ad_break_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_results = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_breaks = json.loads(ad_break_results.output)
        self.assertIsNone(next((item for item in ad_breaks if item["id"] == ad_break_id), None))
        
    def test_delete_asset_ad_break_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--object-key", object_key,
        ])
        
        ad_break = json.loads(result.output)
        ad_break_id = ad_break["id"]
        
        result = self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--id", ad_break_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_asset_ad_break_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "delete-asset-ad-break", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestDeleteAsset(TestAssetBase):
    """Tests for deleting assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_delete_asset_by_id(self):
        """Test asset is deleted successfully"""
        upload_result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/test_files/proxy-image.jpg",
            "--id", self.test_dir_id
        ])

        asset_id = json.loads(upload_result.output)[0]["id"]   

        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--id", asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_asset_list = get_total_asset_list(self, self.test_dir_id)
        
        asset = next((item for item in parent_asset_list if item["id"] == asset_id), None)
        self.assertIsNone(asset)
        
    def test_delete_asset_by_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_asset_by_url(self):
        """Test asset is deleted successfully"""
        upload_result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/test_files/proxy-image.jpg",
            "--id", self.test_dir_id
        ])

        asset_id = json.loads(upload_result.output)[0]["id"]          

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_asset_list = get_total_asset_list(self, self.test_dir_id)
        
        asset = next((item for item in parent_asset_list if item["id"] == self.asset_id), None)
        self.assertIsNone(asset)
        
    def test_delete_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_asset_by_object_key(self):
        """Test asset is deleted successfully"""
        upload_result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/test_files/proxy-image.jpg",
            "--id", self.test_dir_id
        ])

        asset_id = json.loads(upload_result.output)[0]["id"]         

        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        parent_asset_list = get_total_asset_list(self, self.test_dir_id)
        
        asset = next((item for item in parent_asset_list if item["id"] == self.asset_id), None)
        self.assertIsNone(asset)
        
    def test_delete_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_delete_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestDownloadAsset(TestAssetBase):
    """Tests for downloading assets"""

    def test_download_asset_by_id(self):
        """Test asset is downloaded successfully"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        output = result.output.split("[")[1].split("]")[0]
        asset_info = json.loads(f"[{output}]")
        
        self.assertTrue(os.path.exists(asset_info[0]["name"]))
        os.remove(asset_info[0]["name"])
        
    def test_download_asset_by_destination(self):
        """Test asset is downloaded to a destination successfully"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", self.asset_id,
            "--destination", "nomad_media_cli/tests/test_files"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        output = result.output.split("[")[1].split("]")[0]
        asset_info = json.loads(f"[{output}]")
        
        self.assertTrue(os.path.exists(f"nomad_media_cli/tests/test_files/{asset_info[0]['name']}"))
        os.remove(f"nomad_media_cli/tests/test_files/{asset_info[0]['name']}")

    def test_download_asset_by_id_invalid_destination(self):
        """Test invalid destination returns an error"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", self.asset_id,
            "--destination", "invalid-destination"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_download_asset_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_download_asset_by_url(self):
        """Test asset is downloaded successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        self.assertTrue(os.path.exists(asset_details["properties"]["displayName"]))
        
        file_path = os.path.join(os.getcwd(), asset_details["properties"]["displayName"])
        os.remove(file_path)
        
    def test_download_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_download_asset_by_object_key(self):
        """Test asset is downloaded successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        self.assertTrue(os.path.exists(asset_details["properties"]["displayName"]))

        file_path = os.path.join(os.getcwd(), asset_details["properties"]["displayName"])
        os.remove(file_path)
        
        
    def test_download_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_download_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_download_asset_folder(self):
        """Test folder is downloaded successfully"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)

        download_info = result.output.split("[")[1].split("]")[0]
        download_json = json.loads(f"[{download_info}]")
        
        dir_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        dir_info = json.loads(dir_info_result.output)
        dir_path = os.path.join(os.getcwd(), dir_info["properties"]["displayName"])

        for file in download_json:
            if file["assetTypeDisplay"] == "File" and file["downloadStatus"] != "Failed":
                file_path = os.path.join(dir_path, file["name"])
                self.assertTrue(os.path.exists(file_path))
        
        shutil.rmtree(dir_path)

    def test_download_asset_proxy_template_name(self):
        """Test downloading asset with proxy template name"""
        result = self.runner.invoke(cli, [
            "download-assets",
            "--id", "34e4a555-2d84-4ac0-8295-92a7d5f28a1e",
            "--download-proxy",
            "--template-name", "dev-05-default"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        download_info = result.output.split("[")[1].split("]")[0]
        download_json = json.loads(f"[{download_info}]")
        
        dir_info_result = self.runner.invoke(cli, [
            "get-asset-details",
            "--id", self.test_dir_id
        ])
        
        dir_info = json.loads(dir_info_result.output)
        dir_path = os.path.join(os.getcwd(), dir_info["properties"]["displayName"])
        
        for file in download_json:
            if file["assetTypeDisplay"] == "File" and file["downloadStatus"] != "Failed":
                file_path = os.path.join(dir_path, file["name"])
                self.assertTrue(os.path.exists(file_path))
                
        shutil.rmtree(dir_path)
            
        
    def test_download_asset_folder_recursive(self):
        """Test folder is downloaded successfully"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", self.test_dir_id,
            "--recursive"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        download_info = result.output.split("[")[1].split("]")[0]
        download_json = json.loads(f"[{download_info}]")
        
        dir_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        dir_info = json.loads(dir_info_result.output)
        dir_name = dir_info["properties"]["displayName"]
        dir_path = os.path.join(os.getcwd(), dir_name)
        
        for file in download_json:
            if file["assetTypeDisplay"] == "File" and file["downloadStatus"] != "Failed":
                relative_path = dir_name + file["url"].split(dir_name)[1]
                file_path = os.path.join(os.getcwd(), relative_path)
                self.assertTrue(os.path.exists(file_path))

        shutil.rmtree(dir_path)
        
    def test_download_asset_proxy(self):
        """Test folder is downloaded successfully"""
        upload_result =self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/test_files/proxy-image.jpg",
            "--id", self.test_dir_id
        ])

        asset_id = json.loads(upload_result.output)[0]["id"]

        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", asset_id,
            "--download-proxy"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        file_path = os.path.join(os.getcwd(), "proxy-image.jpg")
        self.assertTrue(os.path.exists(file_path))
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", asset_id
        ])
        
        os.remove(file_path)

    def test_download_folder_proxy(self):
        """Test folder is downloaded successfully"""
        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", self.test_dir_id,
            "--download-proxy"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        download_info = result.output.split("[")[1].split("]")[0]
        download_json = json.loads(f"[{download_info}]")
        
        dir_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        dir_info = json.loads(dir_info_result.output)
        dir_name = dir_info["properties"]["displayName"]
        dir_path = os.path.join(os.getcwd(), dir_name)
        
        for file in download_json:
            if file["assetTypeDisplay"] == "File" and file["downloadStatus"] != "Failed":
                relative_path = dir_name + file["url"].split(dir_name)[1]
                file_path = os.path.join(os.getcwd(), relative_path)
                self.assertTrue(os.path.exists(file_path))

        shutil.rmtree(dir_path)
        
    def test_permission_error(self):
        """Test handling of permission errors"""

        def set_read_only(path):
            if platform.system() == "Windows":
                os.system(f'icacls "{path}" /deny Everyone:(W)')
            else:
                os.chmod(path, stat.S_IREAD)

        def reset_permissions(path, original_permissions=None):
            """Restore permissions for a directory."""
            if platform.system() == "Windows":
                os.system(f'icacls "{path}" /grant Everyone:(F)')
            else:
                if original_permissions:
                    os.chmod(path, original_permissions)
                else:
                    os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

        destination_path = "nomad_media_cli/tests"
        original_permissions = os.stat(destination_path).st_mode

        try:
            set_read_only(destination_path)

            result = self.runner.invoke(cli, [
                "download-assets",
                "--id", self.test_dir_id,
                "--destination", destination_path
            ])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("is not writable", result.output)
        finally:
            reset_permissions(destination_path, original_permissions)

    @patch('requests.get')
    def test_connection_failed(self, mock_get):
        """Test handling of network errors during download in the middle of the call"""
        
        def side_effect(*args, **kwargs):
            raise requests.exceptions.ConnectionError("Network error")
        
        mock_get.side_effect = side_effect

        result = self.runner.invoke(cli, [
            "download-assets", 
            "--id", self.test_dir_id,
            "-r"
        ])
        
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Network error", result.output)

        download_info = result.output.split("[")[1].split("]")[0]
        download_json = json.loads(f"[{download_info}]")
        
        dir_info_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        dir_info = json.loads(dir_info_result.output)
        dir_name = dir_info["properties"]["displayName"]
        dir_path = os.path.join(os.getcwd(), dir_name)
        
        for file in download_json:
            if file["assetTypeDisplay"] == "File" and file["downloadStatus"] != "Failed":
                relative_path = dir_name + file["url"].split(dir_name)[1]
                file_path = os.path.join(os.getcwd(), relative_path)
                self.assertTrue(os.path.exists(file_path))

        shutil.rmtree(dir_path)

class TestDuplicateAsset(TestAssetBase):
    """Tests for duplicating assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_duplicate_asset_by_id(self):
        """Test asset is duplicated successfully"""
        result = self.runner.invoke(cli, [
            "duplicate-asset", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_duplicate_asset_by_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "duplicate-asset", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_duplicate_asset_by_url(self):
        """Test asset is duplicated successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "duplicate-asset", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_duplicate_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "duplicate-asset", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_duplicate_asset_by_object_key(self):
        """Test asset is duplicated successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "duplicate-asset", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_duplicate_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "duplicate-asset", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_duplicate_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "duplicate-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAnnotations(TestAssetBase):
    """Tests for getting annotations"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")

    def test_get_annotations(self):
        """Test annotations are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_annotations_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_annotations_by_url(self):
        """Test annotations are retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-annotations", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_annotations_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-annotations", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_annotations_by_object_key(self):
        """Test annotations are retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-annotations", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_annotations_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-annotations", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_annotations_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-annotations", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAssetAdBreaks(TestAssetBase):
    """Tests for getting asset ad breaks"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
    
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_get_asset_ad_breaks(self):
        """Test asset ad breaks are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_ad_breaks_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_ad_breaks_by_url(self):
        """Test asset ad breaks are retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_ad_breaks_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_ad_breaks_by_object_key(self):
        """Test asset ad breaks are retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_ad_breaks_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_ad_breaks_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAssetChildNodes(TestAssetBase):
    """Tests for getting asset child nodes"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_get_asset_child_nodes(self):
        """Test asset child nodes are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset-child-nodes", 
            "--id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_child_nodes_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-child-nodes", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_child_nodes_by_url(self):
        """Test asset child nodes are retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset-child-nodes", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_child_nodes_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-child-nodes", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_child_nodes_by_object_key(self):
        """Test asset child nodes are retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-child-nodes", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_child_nodes_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-child-nodes", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_child_nodes_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-child-nodes", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAssetDetails(TestAssetBase):
    """Tests for getting asset details"""

    def test_get_asset_details(self):
        """Test asset details are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_details_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_details_by_url(self):
        """Test asset details are retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_details_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_details_by_object_key(self):
        """Test asset details are retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_details_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_details_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAssetManifestWithCookies(TestAssetBase):
    """Tests for getting asset manifest with cookies"""

    def test_get_asset_manifest_with_cookies(self):
        """Test asset manifest with cookies is retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset-manifest-with-cookies", 
            "--id", self.asset_id,
            "--cookie-id", "050dc1aa-945f-4f91-81b3-c6dd35d57a3b"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_manifest_with_cookies_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-manifest-with-cookies", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_manifest_with_cookies_by_url(self):
        """Test asset manifest with cookies is retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id,
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset-manifest-with-cookies", 
            "--url", url,
            "--cookie-id", "050dc1aa-945f-4f91-81b3-c6dd35d57a3b"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_manifest_with_cookies_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-manifest-with-cookies", 
            "--url", "invalid-url",
            "--cookie-id", "050dc1aa-945f-4f91-81b3-c6dd35d57a3b"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_manifest_with_cookies_by_object_key(self):
        """Test asset manifest with cookies is retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-manifest-with-cookies", 
            "--object-key", object_key,
            "--cookie-id", "050dc1aa-945f-4f91-81b3-c6dd35d57a3b"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_manifest_with_cookies_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-manifest-with-cookies", 
            "--object-key", object_key,
            "--cookie-id", "050dc1aa-945f-4f91-81b3-c6dd35d57a3b"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_manifest_with_cookies_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-manifest-with-cookies", 
            "--object-key", "invalid-object-key",
            "--cookie-id", "050dc1aa-945f-4f91-81b3-c6dd35d57a3b"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAssetMetadataSummary(TestAssetBase):
    """Tests for getting asset manifest summary"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_get_asset_metadata_summary(self):
        """Test asset manifest summary is retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset-metadata-summary", 
            "--id", self.asset_id
        ])
    
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_metadata_summary_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-metadata-summary", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_metadata_summary_by_url(self):
        """Test asset manifest summary is retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset-metadata-summary", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_metadata_summary_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-metadata-summary", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_metadata_summary_by_object_key(self):
        """Test asset manifest summary is retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-metadata-summary", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_metadata_summary_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-metadata-summary", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_metadata_summary_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-metadata-summary", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAssetParentFolders(TestAssetBase):
    """Tests for getting asset parent folders"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_get_asset_parent_folders(self):
        """Test asset parent folders are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset-parent-folders", 
            "--id", self.asset_id,
            "--page-size", 10
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_parent_folders_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-parent-folders", 
            "--id", "invalid-id",
            "--page-size", 10
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_parent_folders_by_url(self):
        """Test asset parent folders are retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset-parent-folders", 
            "--url", url,
            "--page-size", 10
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_parent_folders_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-parent-folders", 
            "--url", "invalid-url",
            "--page-size", 10
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_parent_folders_by_object_key(self):
        """Test asset parent folders are retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-parent-folders", 
            "--object-key", object_key,
            "--page-size", 10
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_parent_folders_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-parent-folders", 
            "--object-key", object_key,
            "--page-size", 10
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_parent_folders_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-parent-folders", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAssetScreenshotDetails(TestAssetBase):
    """Tests for getting asset screenshot details"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

        screenshot_result = cls.runner.invoke(cli, [
            "create-screenshot-at-timecode",
            "--id", cls.asset_id,
            "--timecode", "00:00:01"
        ])
        
        if screenshot_result.exit_code != 0:
            raise Exception(f"Failed to create screenshot: {screenshot_result.output}")
        
        cls.screenshot_id = json.loads(screenshot_result.output)["id"]
        
    def test_get_asset_screenshot_details(self):
        """Test asset screenshot details are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset-screenshot-details", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_screenshot_details_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-screenshot-details", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_screenshot_details_by_url(self):
        """Test asset screenshot details are retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset-screenshot-details", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_screenshot_details_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-screenshot-details", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_screenshot_details_by_object_key(self):
        """Test asset screenshot details are retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-screenshot-details", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_screenshot_details_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-screenshot-details", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_screenshot_details_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-screenshot-details", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAssetSegmentDetails(TestAssetBase):
    """Tests for getting asset segment details"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_get_asset_segment_details(self):
        """Test asset segment details are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset-segment-details", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_segment_details_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-segment-details", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_segment_details_by_url(self):
        """Test asset segment details are retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset-segment-details", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_segment_details_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-segment-details", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_segment_details_by_object_key(self):
        """Test asset segment details are retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.video_asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-segment-details", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_segment_details_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset-segment-details", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_segment_details_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset-segment-details", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetAsset(TestAssetBase):
    """Tests for getting assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_get_asset_by_id(self):
        """Test asset is retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-asset", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_by_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_by_url(self):
        """Test asset is retrieved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "get-asset", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_by_object_key(self):
        """Test asset is retrieved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "get-asset", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_get_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "get-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetUserUploadParts(TestAssetBase):
    """Tests for getting user upload parts"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")
        
        user_uploads_response = cls.runner.invoke(cli, [
            "get-user-uploads"
        ])
        
        user_uploads = json.loads(user_uploads_response.output)
        if not user_uploads:
            raise unittest.SkipTest("No user uploads found")
        
        cls.user_upload_id = user_uploads[0]["id"]
        
    def test_get_user_upload_parts(self):
        """Test user upload parts are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-user-upload-parts", 
            "--upload-id", self.user_upload_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_get_user_upload_parts_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "get-user-upload-parts", 
            "--upload-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestGetUserUploads(TestAssetBase):
    """Tests for getting user uploads"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_get_user_uploads(self):
        """Test user uploads are retrieved successfully"""
        result = self.runner.invoke(cli, [
            "get-user-uploads"
        ])
        
        self.assertEqual(result.exit_code, 0)

class TestImportAnnotations(TestAssetBase):
    """Tests for importing annotations"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")

    def test_import_annotations(self):
        """Test annotations are imported successfully"""
        result = self.runner.invoke(cli, [
            "import-annotations", 
            "--annotations", '{"startTimeCode": "00:00:01;00"}',
            "--annotations", '{"startTimeCode": "00:00:02;00","endTimeCode": "00:00:03;00"}',
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)

        annotations_result = self.runner.invoke(cli, [
            "get-annotations",
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotations_result.output)
        annotations_found = 0
        for annotation in annotations:
            if annotation["startTimeCode"] == "00:00:02.000":
                self.assertEqual(annotation["endTimeCode"], "00:00:03.000")
                annotations_found += 1
            if annotation["startTimeCode"] == "00:00:01.000":
                self.assertNotIn("endTimeCode", annotation)
                annotations_found += 1
        self.assertEqual(annotations_found, 2)
        
        for annotation in annotations:
            delete_result = self.runner.invoke(cli, [
                "delete-annotation",
                "--id", self.asset_id,
                "--annotation-id", annotation["id"]
            ])
            
            self.assertEqual(delete_result.exit_code, 0)
        
    def test_import_annotations_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "import-annotations", 
            "--annotations", '{"startTimeCode": "00:00:01;00"}',
            "--annotations", '{"startTimeCode": "00:00:02;00","endTimeCode": "00:00:03;00"}',
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_import_annotations_invalid_annotations(self):
        """Test invalid annotations returns an error"""
        result = self.runner.invoke(cli, [
            "import-annotations", 
            "--annotations", "invalid-annotations",
            "--id", self.asset_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_import_annotations_by_url(self):
        """Test annotations are imported successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "import-annotations", 
            "--annotations", '{"startTimeCode": "00:00:01;00"}',
            "--annotations", '{"startTimeCode": "00:00:02;00","endTimeCode": "00:00:03;00"}', 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotations_result = self.runner.invoke(cli, [
            "get-annotations",
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotations_result.output)
        annotations_found = 0
        for annotation in annotations:
            if annotation["startTimeCode"] == "00:00:02.000":
                self.assertEqual(annotation["endTimeCode"], "00:00:03.000")
                annotations_found += 1
            if annotation["startTimeCode"] == "00:00:01.000":
                self.assertNotIn("endTimeCode", annotation)
                annotations_found += 1
        self.assertEqual(annotations_found, 2)
        
        for annotation in annotations:
            delete_result = self.runner.invoke(cli, [
                "delete-annotation",
                "--id", self.asset_id,
                "--annotation-id", annotation["id"]
            ])
            
            self.assertEqual(delete_result.exit_code, 0)
        
    def test_import_annotations_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "import-annotations", 
            "--annotations", '{"startTimeCode": "00:00:01;00"}',
            "--annotations", '{"startTimeCode": "00:00:02;00","endTimeCode": "00:00:03;00"}',
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_import_annotations_by_object_key(self):
        """Test annotations are imported successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "import-annotations", 
            "--annotations", '{"startTimeCode": "00:00:01;00"}',
            "--annotations", '{"startTimeCode": "00:00:02;00","endTimeCode": "00:00:03;00"}',
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotations_result = self.runner.invoke(cli, [
            "get-annotations",
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotations_result.output)
        annotations_found = 0
        for annotation in annotations:
            if annotation["startTimeCode"] == "00:00:02.000":
                self.assertEqual(annotation["endTimeCode"], "00:00:03.000")
                annotations_found += 1
            if annotation["startTimeCode"] == "00:00:01.000":
                self.assertNotIn("endTimeCode", annotation)
                annotations_found += 1
        self.assertEqual(annotations_found, 2)
        
        for annotation in annotations:
            delete_result = self.runner.invoke(cli, [
                "delete-annotation",
                "--id", self.asset_id,
                "--annotation-id", annotation["id"]
            ])
            
            self.assertEqual(delete_result.exit_code, 0)
        
    def test_import_annotations_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "import-annotations", 
            "--annotations", '{"startTimeCode": "00:00:01;00"}',
            "--annotations", '{"startTimeCode": "00:00:02;00","endTimeCode": "00:00:03;00"}',
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_import_annotations_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "import-annotations", 
            "--annotations", '{"startTimeCode": "00:00:01;00"}',
            "--annotations", '{"startTimeCode": "00:00:02;00","endTimeCode": "00:00:03;00"}',
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestIndexAsset(TestAssetBase):
    """Tests for indexing assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_index_asset_by_id(self):
        """Test asset is indexed successfully"""
        result = self.runner.invoke(cli, [
            "index-asset", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_index_asset_by_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "index-asset", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_index_asset_by_url(self):
        """Test asset is indexed successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "index-asset", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_index_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "index-asset", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_index_asset_by_object_key(self):
        """Test asset is indexed successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "index-asset", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_index_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "index-asset", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_index_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "index-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestListAssets(TestAssetBase):
    """Tests for listing assets"""
    
    def test_list_assets_file_by_id(self):
        
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json["items"], list))
            self.assertTrue(len(output_json["items"]) > 0)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
            
    def test_list_assets_folder_by_id(self):
        
        asset_parent_id = self.test_dir_id

        result = self.runner.invoke(cli, [
            "list-assets", 
            "--id", asset_parent_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json["items"], list))
            self.assertTrue(len(output_json["items"]) > 0)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
            
    def test_list_assets_folder_recursive(self):
        
        asset_parent_id = self.test_dir_id

        result = self.runner.invoke(cli, [
            "list-assets", 
            "--id", asset_parent_id,
            "--recursive"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json["items"], list))
            self.assertTrue(len(output_json["items"]) > 0)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_assets_by_id_invalid(self):
        
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_list_assets_file_by_url(self):
        
        list_buckets_result = self.runner.invoke(cli, ["list-buckets"])
        buckets = json.loads(list_buckets_result.output)
        
        if len(buckets) == 0:
            self.skipTest("No buckets available")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
            
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json["items"], list))
            self.assertTrue(len(output_json["items"]) > 0)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
            
    def test_list_assets_folder_by_url(self):
            
        asset_parent_id = self.test_dir_id
        asset_parent_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", asset_parent_id
        ])
        
        asset_parent_details = json.loads(asset_parent_details_result.output)
        url = asset_parent_details["properties"]["url"]
            
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json["items"], list))
            self.assertTrue(len(output_json["items"]) > 0)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_assets_by_url_invalid(self):
        
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            
    def test_list_assets_by_file_object_key(self):
 
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
            
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json["items"], list))
            self.assertTrue(len(output_json["items"]) > 0)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
            
    def test_list_assets_by_folder_object_key(self):
 
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json["items"], list))
            self.assertTrue(len(output_json["items"]) > 0)
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
            
    def test_list_assets_by_object_key_no_bucket(self):
 
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            
    def test_list_assets_by_object_key_invalid(self):
        
        result = self.runner.invoke(cli, [
            "list-assets", 
            "--object-key", "invalid-object-key"
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_list_assets_page_size(self):
        result = self.runner.invoke(cli, [
            "list-assets",
            "--id", self.asset_id,
            "--page-size", "10",
            "--page-offset", "0"
        ])
        self.assertEqual(result.exit_code, 0)
        output = json.loads(result.output)
        self.assertTrue(len(output["items"]) <= 10)
        
    def test_list_assets_invalid_page_size(self):
        result = self.runner.invoke(cli, [
            "list-assets",
            "--id", self.asset_id,
            "--page-size", "-1"
        ])
        self.assertNotEqual(result.exit_code, 0)

    def test_list_assets_page_offset(self):
        result = self.runner.invoke(cli, [
            "list-assets",
            "--id", self.asset_id,
            "--page-size", "1",
            "--page-offset", "0"
        ])
        self.assertEqual(result.exit_code, 0)

    def test_list_assets_invalid_offset(self):
        result = self.runner.invoke(cli, [
            "list-assets",
            "--id", self.asset_id,
            "--page-offset", "-1"
        ])
        self.assertNotEqual(result.exit_code, 0)
        
    def test_list_assets_page_offset_token(self):

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        parent_id = asset_details["properties"]["parentId"]        

        result = self.runner.invoke(cli, [
            "list-assets",
            "--id", parent_id,
            "--page-size", "1",
        ])
        
        result_json = json.loads(result.output)
        next_page_offset = result_json.get("nextPageOffset")

        if not next_page_offset:
            self.skipTest("No next page offset")
            
        result = self.runner.invoke(cli, [
            "list-assets",
            "--id", self.asset_id,
            "--page-offset-token", next_page_offset
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_list_asset_page_offset_token_invalid(self):
        result = self.runner.invoke(cli, [
            "list-assets",
            "--id", self.asset_id,
            "--page-offset-token", "invalid-token"
        ])
        self.assertNotEqual(result.exit_code, 0)
    
    def test_list_assets_sorting(self):
        result = self.runner.invoke(cli, [
            "list-assets",
            "--id", self.asset_id,
            "--order-by", "name",
            "--order-by-type", "desc"
        ])
        self.assertEqual(result.exit_code, 0)
        output = json.loads(result.output)
        
        names = [item["name"] for item in output["items"]]
        self.assertEqual(names, sorted(names, reverse=True))
    
    def test_list_assets_missing_params(self):
        result = self.runner.invoke(cli, ["list-assets"])
        self.assertNotEqual(result.exit_code, 0)

class TestLocalRestoreAsset(TestAssetBase):
    """Tests for restoring assets from local"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")

    def test_local_restore_asset_by_id(self):
        """Test asset is restored successfully"""
        result = self.runner.invoke(cli, [
            "local-restore-asset", 
            "--profile", "s3-1",
            "--id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_local_restore_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "local-restore-asset", 
            "--profile", "s3-1",
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_local_restore_asset_by_url(self):
        """Test asset is restored successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "local-restore-asset", 
            "--profile", "s3-1",
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_local_restore_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "local-restore-asset", 
            "--profile", "s3-1",
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_local_restore_asset_by_object_key(self):
        """Test asset is restored successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "local-restore-asset", 
            "--profile", "s3-1",
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_local_restore_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.test_dir_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "local-restore-asset", 
            "--profile", "s3-1",
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_local_restore_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "local-restore-asset", 
            "--profile", "s3-1",
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestMoveAsset(TestAssetBase):
    """Tests for moving assets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")
        
        create_folder_result = cls.runner.invoke(cli, [
            "create-folder-asset",
            "--display-name", "test_folder",
            "--parent-id", cls.test_dir_id
        ])
        
        test_folder_output = create_folder_result.output.strip()
        cls.test_folder_id = json.loads(test_folder_output)["id"]
    
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        
        cls.runner.invoke(cli, [
            "delete-asset", 
            "--id", cls.test_folder_id
        ])
        
    def test_move_asset_by_id(self):
        """Test asset is moved successfully"""
        result = self.runner.invoke(cli, [
            "move-asset", 
            "--id", self.asset_id,
            "--destination-folder-id", self.test_folder_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        test_folder_assets = get_total_asset_list(self, self.test_folder_id)
        self.assertIn(self.asset_id, [asset["id"] for asset in test_folder_assets])
        
        self.runner.invoke(cli, [
            "move-asset", 
            "--id", self.asset_id,
            "--destination-folder-id", self.test_dir_id
        ])
        
    def test_move_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "move-asset", 
            "--id", "invalid-id",
            "--destination-folder-id", self.test_folder_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_move_asset_by_url(self):
        """Test asset is moved successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "move-asset", 
            "--url", url,
            "--destination-folder-id", self.test_folder_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        test_folder_assets = get_total_asset_list(self, self.test_folder_id)
        self.assertIn(self.asset_id, [asset["id"] for asset in test_folder_assets])
        
        self.runner.invoke(cli, [
            "move-asset", 
            "--id", self.asset_id,
            "--destination-folder-id", self.test_dir_id
        ])
        
    def test_move_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "move-asset", 
            "--url", "invalid-url",
            "--destination-folder-id", self.test_folder_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_move_asset_by_object_key(self):
        """Test asset is moved successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "move-asset", 
            "--object-key", object_key,
            "--destination-folder-id", self.test_folder_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        test_folder_assets = get_total_asset_list(self, self.test_folder_id)
        self.assertIn(self.asset_id, [asset["id"] for asset in test_folder_assets])
        
        self.runner.invoke(cli, [
            "move-asset", 
            "--id", self.asset_id,
            "--destination-folder-id", self.test_dir_id
        ])
        
    def test_move_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "move-asset", 
            "--object-key", object_key,
            "--destination-folder-id", self.test_folder_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_move_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "move-asset", 
            "--object-key", "invalid-object-key",
            "--destination-folder-id", self.test_folder_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestRecordsAssetTrackingBeacon(TestAssetBase):
    """Tests for recording asset tracking beacon"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")

    def test_record_asset_tracking_beacon(self):
        """Test asset tracking beacon is recorded successfully"""
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--id", self.asset_id,
            "--tracking-event", "FirstQuartile",
            "--live-channel-id", self.live_channel_id,
            "--second", 1
        ])

        self.assertEqual(result.exit_code, 0)
        
    def test_record_asset_tracking_beacon_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--id", "invalid-id",
            "--tracking-event", "FirstQuartile",
            "--live-channel-id", self.live_channel_id,
            "--second", 1
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_record_asset_tracking_beacon_invalid_event(self):
        """Test invalid event returns an error"""
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--id", self.asset_id,
            "--tracking-event", "invalid-event",
            "--live-channel-id", self.live_channel_id,
            "--second", 1
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_record_asset_tracking_beacon_invalid_live_channel_id(self):
        """Test invalid live channel ID returns an error"""
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--id", self.asset_id,
            "--tracking-event", "FirstQuartile",
            "--live-channel-id", "invalid-id",
            "--second", 1
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_record_asset_tracking_beacon_by_url(self):
        """Test asset tracking beacon is recorded successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--url", url,
            "--tracking-event", "FirstQuartile",
            "--live-channel-id", self.live_channel_id,
            "--second", 1
        ])

        self.assertEqual(result.exit_code, 0)
        
    def test_record_asset_tracking_beacon_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--url", "invalid-url",
            "--tracking-event", "FirstQuartile",
            "--live-channel-id", self.live_channel_id,
            "--second", 1
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_record_asset_tracking_beacon_by_object_key(self):
        """Test asset tracking beacon is recorded successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--object-key", object_key,
            "--tracking-event", "FirstQuartile",
            "--live-channel-id", self.live_channel_id,
            "--second", 1
        ])

        self.assertEqual(result.exit_code, 0)
        
    def test_record_asset_tracking_beacon_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--object-key", object_key,
            "--tracking-event", "FirstQuartile",
            "--live-channel-id", self.live_channel_id,
            "--second", 1
        ])

        self.assertNotEqual(result.exit_code, 0)
        
    def test_record_asset_tracking_beacon_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "records-asset-tracking-beacon", 
            "--object-key", "invalid-object-key",
            "--tracking-event", "FirstQuartile",
            "--live-channel-id", self.live_channel_id,
            "--second", 1
        ])

        self.assertNotEqual(result.exit_code, 0)
        
class TestRegisterAsset(TestAssetBase):
    """Tests for registering assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")
    
    def test_register_asset_by_id(self):
        """Test asset is registered successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "register-asset", 
            "--id", self.asset_id,
            "--bucket-name", self.config["bucket"],
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_register_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "register-asset", 
            "--id", "invalid-id",
            "--bucket-name", self.config["bucket"],
            "--object-key", "test"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_register_asset_by_url(self):
        """Test asset is registered successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]

        result = self.runner.invoke(cli, [
            "register-asset", 
            "--url", url,
            "--bucket-name", self.config["bucket"],
            "--object-key", "test"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_register_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "register-asset", 
            "--url", "invalid-url",
            "--bucket-name", self.config["bucket"],
            "--object-key", "test"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_register_asset_by_id_add_tag_by_name(self):
        """Test asset is registered successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        tag_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "tag"
        ])

        tag_contents = json.loads(tag_contents.output)        

        result = self.runner.invoke(cli, [
            "register-asset", 
            "--id", self.asset_id,
            "--bucket-name", self.config["bucket"],
            "--object-key", object_key,
            "--tag-names", tag_contents[0]["title"],
            "--tag-names", tag_contents[1]["title"]
        ])

        self.assertEqual(result.exit_code, 0)

        asset_info = self.runner.invoke(cli, [
            "get-asset-details",
            "--id", self.asset_id
        ])
        
        asset_info = json.loads(asset_info.output)
        tags = asset_info["tags"]
        self.assertTrue(any(tag_contents[0]["title"] in tag["title"] for tag in tags))
        self.assertTrue(any(tag_contents[1]["title"] in tag["title"] for tag in tags))
        

class TestReprocessAsset(TestAssetBase):
    """Tests for reprocessing assets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_reprocess_asset_by_id(self):
        """Test asset is reprocessed successfully"""
        result = self.runner.invoke(cli, [
            "reprocess-asset", 
            "--target-ids", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_reprocess_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "reprocess-asset", 
            "--target-ids", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_reprocess_asset_by_url(self):
        """Test asset is reprocessed successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "reprocess-asset", 
            "--target-urls", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_reprocess_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "reprocess-asset", 
            "--target-urls", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_reprocess_asset_by_object_key(self):
        """Test asset is reprocessed successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "reprocess-asset", 
            "--target-object-keys", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_reprocess_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "reprocess-asset", 
            "--target-object-keys", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_reprocess_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "reprocess-asset", 
            "--target-object-keys", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestRestoreAsset(TestAssetBase):
    """Tests for restoring assets"""    
    
    def test_restore_asset_by_id(self):
        """Test asset is restored successfully"""
        result = self.runner.invoke(cli, [
            "restore-asset", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_restore_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "restore-asset", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_restore_asset_by_url(self):
        """Test asset is restored successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "restore-asset", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_restore_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "restore-asset", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_restore_asset_by_object_key(self):
        """Test asset is restored successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "restore-asset", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)

    def test_restore_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "restore-asset", 
            "--object-key", object_key
        ])

        self.assertNotEqual(result.exit_code, 0)
        
    def test_restore_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "restore-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestShareAsset(TestAssetBase):
    """Tests for sharing assets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")

    def test_share_asset_by_id(self):
        """Test asset is shared successfully"""
        result = self.runner.invoke(cli, [
            "share-asset", 
            "--id", self.asset_id,
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_share_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "share-asset", 
            "--id", "invalid-id",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_share_asset_by_url(self):
        """Test asset is shared successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "share-asset", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_share_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "share-asset", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_share_asset_by_object_key(self):
        """Test asset is shared successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "share-asset", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_share_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "share-asset", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_share_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "share-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestStartWorkflow(TestAssetBase):
    """Tests for starting workflows"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_start_workflow(self):
        """Test workflow is started successfully"""
        result = self.runner.invoke(cli, [
            "start-workflow", 
            "--target-ids", self.asset_id,
            "--action-arguments", "{'workflowName': 'ExternalTranslation'}"
        ])

        self.assertEqual(result.exit_code, 0)
        
    def test_start_workflow_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "start-workflow", 
            "--target-ids", "invalid-id",
            "--action-arguments", "{'workflowName': 'ExternalTranslation'}"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_start_workflow_invalid_workflow(self):
        """Test invalid workflow returns an error"""
        result = self.runner.invoke(cli, [
            "start-workflow", 
            "--target-ids", self.asset_id,
            "--action-arguments", "{'workflowName': 'invalid-workflow'}"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_start_workflow_by_url(self):
        """Test workflow is started successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "start-workflow", 
            "--target-urls", url,
            "--action-arguments", "{'workflowName': 'ExternalTranslation'}"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_start_workflow_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "start-workflow", 
            "--target-urls", "invalid-url",
            "--action-arguments", "{'workflowName': 'ExternalTranslation'}"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_start_workflow_by_object_key(self):
        """Test workflow is started successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "start-workflow", 
            "--target-object-keys", object_key,
            "--action-arguments", "{'workflowName': 'ExternalTranslation'}"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_start_workflow_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "start-workflow", 
            "--target-object-keys", object_key,
            "--action-arguments", "{'workflowName': 'ExternalTranslation'}"
        ])

        self.assertNotEqual(result.exit_code, 0)
        
    def test_start_workflow_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "start-workflow", 
            "--target-object-keys", "invalid-object-key",
            "--action-arguments", "{'workflowName': 'ExternalTranslation'}"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
      
class TestShareAsset(TestAssetBase):
    """Tests for sharing assets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")

    def test_share_asset_by_id(self):
        """Test asset is shared successfully"""
        result = self.runner.invoke(cli, [
            "share-asset", 
            "--id", self.asset_id,
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_share_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "share-asset", 
            "--id", "invalid-id",
            "--sync-direction", "nomad-to-local"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_sync_assets_invalid_source(self):
        """Test invalid source returns an error"""
        result = self.runner.invoke(cli, [
            "sync-assets", 
            "--source", "nomad_media_cli/tests/test_files/invalid-file",
            "--id", self.test_files_id,
            "--sync-direction", "nomad-to-local"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_sync_assets_invalid_sync_direction(self):
        """Test invalid sync direction returns an error"""
        result = self.runner.invoke(cli, [
            "sync-assets", 
            "--source", "nomad_media_cli/tests/test_files",
            "--id", self.test_files_id,
            "--sync-direction", "invalid-sync-direction"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_sync_assets_invalid_url(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "sync-assets", 
            "--source", "nomad_media_cli/tests/test_files",
            "--url", "invalid-url",
            "--sync-direction", "local-to-nomad"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_sync_assets_invalid_object_key(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "sync-assets", 
            "--source", "nomad_media_cli/tests/test_files",
            "--object-key", "invalid-object-key",
            "--sync-direction", "local-to-nomad"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_sync_assets_invalid_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        result = self.runner.invoke(cli, [
            "sync-assets", 
            "--source", "nomad_media_cli/tests/test_files",
            "--object-key", "invalid-object-key",
            "--sync-direction", "local-to-nomad"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_sync_assets_very_large(self):
        """Test syncing a very large number of files"""
        try:
            os.makedirs("nomad_media_cli/tests/test_files/Content", exist_ok=True)

            sync_result = self.runner.invoke(cli, [
                "sync-assets", 
                "--source", "nomad_media_cli/tests/test_files/Content",
                "--id", self.content_dir_id,
                "--sync-direction", "nomad-to-local",
                "--threads", "16",
            ])
            
            self.assertEqual(sync_result.exit_code, 0)
            
            list_dir_assets = get_total_asset_list(self, self.content_dir_id)
            check_dir_structure(self, list_dir_assets, "nomad_media_cli/tests/test_files")
        finally:
            os.removedirs("nomad_media_cli/tests/test_files/Content")  
class TestTranscribeAsset(TestAssetBase):
    """Tests for transcribing assets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")
        
    def test_transcribe_asset_by_id(self):
        """Test asset is transcribed successfully"""

class TestUpdateAnnotation(TestAssetBase):
    """Tests for updating annotations"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "portal":
            raise unittest.SkipTest("API type is not portal")
        
        create_annotation_result = cls.runner.invoke(cli, [
            "create-annotation", 
            "--id", cls.asset_id,
            "--start-time-code", "00:00:00:01",
        ])
        
        annotation = json.loads(create_annotation_result.output)
        cls.annotation_id = annotation["id"]
        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        
        cls.runner.invoke(cli, [
            "delete-annotation", 
            "--id", cls.annotation_id
        ])
        
    def test_update_annotation(self):
        """Test annotation is updated successfully"""
        result = self.runner.invoke(cli, [
            "update-annotation", 
            "--id", self.asset_id,
            "--annotation-id", self.annotation_id,
            "--start-time-code", "00:00:00:02",
        ])

        self.assertEqual(result.exit_code, 0)
        
    def test_update_annotation_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "update-annotation", 
            "--id", "invalid-id",
            "--annotation-id", self.annotation_id,
            "--start-time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_annotation_by_url(self):
        """Test annotation is updated successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "update-annotation", 
            "--url", url,
            "--annotation-id", self.annotation_id,
            "--start-time-code", "00:00:00:03",
        ])
        
        self.assertEqual(result.exit_code, 0)
        
    def test_update_annotation_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "update-annotation", 
            "--url", "invalid-url",
            "--annotation-id", self.annotation_id,
            "--start-time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_annotation_by_object_key(self):
        """Test annotation is updated successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "update-annotation", 
            "--object-key", object_key,
            "--annotation-id", self.annotation_id,
            "--start-time-code", "00:00:00:04",
        ])

        self.assertEqual(result.exit_code, 0)
        
    def test_update_annotation_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        annotation_details_result = self.runner.invoke(cli, [
            "get-annotation-details", 
            "--id", self.annotation_id
        ])

        annotation_details = json.loads(annotation_details_result.output)
        object_key = annotation_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "update-annotation", 
            "--object-key", object_key,
            "--start-time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_annotation_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "update-annotation", 
            "--object-key", "invalid-object-key",
            "--start-time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_annotation_add_metadata(self):
        """Test annotation is updated successfully"""
        result = self.runner.invoke(cli, [
            "update-annotation",
            "--id", self.asset_id,
            "--annotation-id", self.annotation_id,
            "--start-time-code", "00:00:00;05",
            "--title", "test_annotation",
            "--summary", "test_annotation_summary",
            "--description", "test_annotation_description"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        annotation_results = self.runner.invoke(cli, [
            "get-annotations", 
            "--id", self.asset_id
        ])
        
        annotations = json.loads(annotation_results.output)
        self.assertTrue(annotations)
    
        annotation = next((annotation for annotation in annotations if annotation["startTimeCode"] == "00:00:00;05"), None)
        self.assertTrue(annotation)
        
        self.assertEqual(annotation["properties"]["title"], "test_annotation")
        self.assertEqual(annotation["properties"]["summary"], "test_annotation_summary")
        self.assertEqual(annotation["properties"]["description"], "test_annotation_description")

class TestUpdateAssetAdBreak(TestAssetBase):
    """Tests for updating asset ad breaks"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

        create_ad_break_result = cls.runner.invoke(cli, [
            "create-asset-ad-break", 
            "--id", cls.asset_id,
            "--time-code", "00:00:05;00",
        ])
        
        ad_break_info = json.loads(create_ad_break_result.output)
        
        ad_breaks_results = cls.runner.invoke(cli, [
            "get-asset-ad-breaks",
            "--id", cls.asset_id
        ])
        
        ad_breaks = json.loads(ad_breaks_results.output)
        cls.ad_break_id = next((item for item in ad_breaks if item["timeCode"] == "00:00:05;00"), None)["id"]
        
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        
        cls.runner.invoke(cli, [
            "delete-ad-break", 
            "--id", cls.ad_break_id
        ])
        
    def test_update_asset_ad_break(self):
        """Test ad break is updated successfully"""
        result = self.runner.invoke(cli, [
            "update-asset-ad-break", 
            "--id", self.asset_id,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:02",
        ])

        self.assertEqual(result.exit_code, 0)

        ad_break_details_result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])

        ad_break_details = json.loads(ad_break_details_result.output)
        self.assertIsNotNone(next((item for item in ad_break_details if item["timeCode"] == "00:00:00:02"), None))
        
    def test_update_asset_ad_break_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-ad-break", 
            "--id", "invalid-id",
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_upldate_asset_ad_break_invalid_ad_break_id(self):
        """Test invalid ad break ID returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-ad-break",
            "--id", self.asset_id,
            "--ad-break-id", "invalid-ad-break-id",
            "--time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_update_asset_ad_break_by_url(self):
        """Test ad break is updated successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "update-asset-ad-break", 
            "--url", url,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:03",
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_details_result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_break_details = json.loads(ad_break_details_result.output)
        self.assertIsNotNone(next((item for item in ad_break_details if item["timeCode"] == "00:00:00:03"), None))
        
    def test_update_asset_ad_break_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-ad-break", 
            "--url", "invalid-url",
            "--time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_update_asset_ad_break_by_object_key(self):
        """Test ad break is updated successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "update-asset-ad-break",
            "--object-key", object_key,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:04",
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_details_result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])

        ad_break_details = json.loads(ad_break_details_result.output)
        self.assertIsNotNone(next((item for item in ad_break_details if item["timeCode"] == "00:00:00:04"), None))

    def test_update_asset_ad_break_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        ad_break_details_result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])

        ad_break_details = json.loads(ad_break_details_result.output)
        object_key = ad_break_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "update-asset-ad-break",
            "--object-key", object_key,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_ad_break_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-ad-break",
            "--object-key", "invalid-object-key",
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:02",
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_update_asset_ad_break_by_id_add_tag_by_name(self):
        """Test ad break is updated successfully"""
        tag_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "tag"
        ])
        
        tag_contents = json.loads(tag_contents.output)
        
        result = self.runner.invoke(cli, [
            "update-asset-ad-break", 
            "--id", self.asset_id,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:05",
            "--tag-names", tag_contents[0]["title"],
            "--tag-names", tag_contents[1]["title"]
        ])
        
        self.assertEqual(result.exit_code, 0)
        ad_break_details_result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_break_details = json.loads(ad_break_details_result.output)
        tags = ad_break_details["tags"]
        
        self.assertTrue(any(tag_contents[0]["title"] in tag["title"] for tag in tags))
        self.assertTrue(any(tag_contents[1]["title"] in tag["title"] for tag in tags))
        
    def test_update_asset_ad_break_by_id_add_tag_by_name_invalid(self):
        """Test invalid tag name returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-ad-break", 
            "--id", self.asset_id,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:05",
            "--tag-names", "invalid-tag-name"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_ad_break_by_id_add_tag_by_id(self):
        """Test ad break is updated successfully"""
        tag_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "tag"
        ])
        
        tag_contents = json.loads(tag_contents.output)
        
        result = self.runner.invoke(cli, [
            "update-asset-ad-break", 
            "--id", self.asset_id,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:06",
            "--tag-ids", tag_contents[0]["id"],
            "--tag-ids", tag_contents[1]["id"]
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_details_result = self.runner.invoke(cli, [
            "get-asset-ad-breaks", 
            "--id", self.asset_id
        ])
        
        ad_break_details = json.loads(ad_break_details_result.output)
        tags = ad_break_details["tags"]
        
        self.assertTrue(any(tag_contents[0]["title"] in tag["title"] for tag in tags))
        self.assertTrue(any(tag_contents[1]["title"] in tag["title"] for tag in tags))
        
    def test_update_asset_ad_break_by_id_add_tag_by_id_invalid(self):
        """Test invalid tag ID returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-ad-break",
            "--id", self.asset_id,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:06",
            "--tag-ids", "invalid-tag-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_ad_break_by_id_add_label_by_name(self):
        """Test ad break is updated successfully"""
        label_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "label"
        ])
        
        label_contents = json.loads(label_contents.output)
        
        result = self.runner.invoke(cli, [
            "update-asset-ad-break",
            "--id", self.asset_id,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:07",
            "--label-names", label_contents[0]["title"],
            "--label-names", label_contents[1]["title"]
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_details_result = self.runner.invoke(cli, [
            "get-asset-ad-breaks",
            "--id", self.asset_id
        ])
        
        ad_break_details = json.loads(ad_break_details_result.output)
        
        labels = ad_break_details["labels"]
        
        self.assertTrue(any(label_contents[0]["title"] in label["title"] for label in labels))
        self.assertTrue(any(label_contents[1]["title"] in label["title"] for label in labels))
        
    def test_update_asset_ad_break_by_id_add_label_by_name_invalid(self):
        """Test invalid label name returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-ad-break",
            "--id", self.asset_id,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:07",
            "--label-names", "invalid-label-name"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_ad_break_by_id_add_label_by_id(self):
        """Test ad break is updated successfully"""
        label_contents = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "label"
        ])
        
        label_contents = json.loads(label_contents.output)
        
        result = self.runner.invoke(cli, [
            "update-asset-ad-break",
            "--id", self.asset_id,
            "--ad-break-id", self.ad_break_id,
            "--time-code", "00:00:00:08",
            "--label-ids", label_contents[0]["id"],
            "--label-ids", label_contents[1]["id"]
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        ad_break_details_result = self.runner.invoke(cli, [
            "get-asset-ad-breaks",
            "--id", self.asset_id
        ])
        
        ad_break_details = json.loads(ad_break_details_result.output)
        labels = ad_break_details["labels"]
        
        self.assertTrue(any(label_contents[0]["title"] in label["title"] for label in labels))
        self.assertTrue(any(label_contents[1]["title"] in label["title"] for label in labels))
        
class TestUpdateAssetLanguage(TestAssetBase):
    """Tests for updating asset language"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_update_asset_language(self):
        """Test language is updated successfully"""
        result = self.runner.invoke(cli, [
            "update-asset-language", 
            "--id", self.asset_id,
            "--language-id", "4053cade-cbc9-4920-b32b-35e4a5047e51"
        ])
        
        self.assertEqual(result.exit_code, 0)

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        time.sleep(5)

        asset_details = json.loads(asset_details_result.output)
        self.assertEqual(asset_details["properties"]["languageId"], "4053cade-cbc9-4920-b32b-35e4a5047e51")
        
    def test_update_asset_language_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-language", 
            "--id", "invalid-id",
            "--language-id", "4053cade-cbc9-4920-b32b-35e4a5047e51"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_language_invalid_language_id(self):
        """Test invalid language ID returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-language", 
            "--id", self.asset_id,
            "--language-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_language_by_url(self):
        """Test language is updated successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "update-asset-language", 
            "--url", url,
            "--language-id", "4053cade-cbc9-4920-b32b-35e4a5047e51"
        ])
        
        self.assertEqual(result.exit_code, 0)

        time.sleep(5)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        self.assertEqual(asset_details["properties"]["languageId"], "4053cade-cbc9-4920-b32b-35e4a5047e51")
        
    def test_update_asset_language_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-language", 
            "--url", "invalid-url",
            "--language-id", "4053cade-cbc9-4920-b32b-35e4a5047e51"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_update_asset_language_by_object_key(self):
        """Test language is updated successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "update-asset-language", 
            "--object-key", object_key,
            "--language-id", "4053cade-cbc9-4920-b32b-35e4a5047e51"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        time.sleep(5)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        self.assertEqual(asset_details["properties"]["languageId"], "4053cade-cbc9-4920-b32b-35e4a5047e51")
        
    def test_update_asset_language_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "update-asset-language", 
            "--object-key", object_key,
            "--language-id", "4053cade-cbc9-4920-b32b-35e4a5047e51"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_language_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset-language", 
            "--object-key", "invalid-object-key",
            "--language-id", "4053cade-cbc9-4920-b32b-35e4a5047e51"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestUpdateAsset(TestAssetBase):
    """Tests for updating assets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")
        
        for i in range(10):
            try:
                result = cls.runner.invoke(cli, [
                    "get-asset-details",
                    "--id", cls.asset_id
                ])
                
                asset_details = json.loads(result.output)
                if asset_details["properties"]["statusName"] == "Available":
                    break
                
            except:
                time.sleep(i ** 3)
                continue
        
    def test_update_asset_by_id(self):
        """Test asset is updated successfully"""
        result = self.runner.invoke(cli, [
            "update-asset", 
            "--id", self.asset_id,
            "--display-name", "test",
            "--display-date", "2023-10-01",
            "--available-start-date", "2023-10-01",
            "--available-end-date", "2023-10-01",
            "--custom-properties", '{"key": "value"}'
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        
        self.assertEqual(asset_details["properties"]["displayName"], "test")
        self.assertEqual(asset_details["properties"]["displayDate"], "2023-10-01T00:00:00Z")
        self.assertEqual(asset_details["availability"][0]["availableStartDate"], "2023-10-01T00:00:00Z")
        self.assertEqual(asset_details["availability"][0]["availableEndDate"], "2023-10-01T00:00:00Z")
        self.assertEqual("key" in asset_details["customAttributes"], True)
        
    def test_update_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset", 
            "--id", "invalid-id",
            "--display-name", "test"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_by_url(self):
        """Test asset is updated successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "update-asset", 
            "--url", url,
            "--display-name", "test1"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        self.assertEqual(asset_details["properties"]["displayName"], "test1")
        
    def test_update_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset", 
            "--url", "invalid-url",
            "--display-name", "test"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_update_asset_by_object_key(self):
        """Test asset is updated successfully"""
        bucket = self.config.get("bucket")
        if not bucket:
            self.skipTest("No default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "update-asset", 
            "--object-key", object_key,
            "--display-name", "test2"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        self.assertEqual(asset_details["properties"]["displayName"], "test2")

    def test_update_asset_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "update-asset", 
            "--object-key", object_key,
            "--display-name", "test"
        ])

        self.assertNotEqual(result.exit_code, 0)
        
    def test_update_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "update-asset", 
            "--object-key", "invalid-object-key",
            "--display-name", "test"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestUploadAsset(TestAssetBase):
    """Tests for uploading assets"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")

    def test_upload_asset_by_id(self):
        """Test asset is uploaded successfully"""
        result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/test_files/vid1.mp4",
            "--id", self.test_dir_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        list_dir_assets = get_total_asset_list(self, self.test_dir_id)
        
        asset_id = next((item["id"] for item in list_dir_assets if item["name"] == "vid1.mp4"), None)
        self.assertIsNotNone(asset_id)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", asset_id
        ])
        
    def test_upload_asset_invalid_file(self):
        """Test invalid file returns an error"""
        result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/test_files/invalid-file",
            "--id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_upload_asset_empty_file(self):
        """Test empty file returns an error"""
        result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/__init__.py",
            "--id", self.test_dir_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_upload_asset_invalid_id(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/test_files/vid1.mp4",
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_upload_asset_directory_flat(self):
        """Test uploading a directory of files with no subdirectories"""
        test_path = "nomad_media_cli/commands/common/content_metadata"        

        result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", test_path,
            "--id", self.test_dir_id,
            "-r"
        ])
        
        self.assertEqual(result.exit_code, 0)
        num_files_in_dir = sum([len(files) + len(dirs) for _, dirs, files in os.walk(test_path)])
        
        list_assets_parent_result = get_total_asset_list(self, self.test_dir_id)
        parent_folders = [item for item in list_assets_parent_result if item["assetTypeDisplay"] == "Folder"]
        
        test_path_end = test_path.split("/")[-1]
        dir_id = next((item["id"] for item in parent_folders if test_path_end in item["name"]), None)
        
        if not dir_id:
            self.fail("Directory not found")
        
        items = get_total_asset_list(self, dir_id)
        self.assertEqual(len(items), num_files_in_dir)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", dir_id
        ])
        
        time.sleep(10)
        
        delete_asset_details = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", dir_id
        ])
        
        self.assertNotEqual(delete_asset_details.exit_code, 0)
        
    def test_upload_asset_directory_small(self):
        """Test uploading a directory of files with a small number of files"""
        dir_path = "nomad_media_cli/tests"        

        result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", dir_path,
            "--id", self.test_dir_id,
            "-r",
            "--num_files", 8
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        items = get_total_asset_list(self, self.test_dir_id)
        dir_id = next((item["id"] for item in items if item["name"] == f"{dir_path.split("/")[-1]}/"), None)
        self.asset_upload_id = dir_id      

        items = get_total_asset_list(self, dir_id)

        check_dir_structure(self, items, dir_path)
        
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--id", dir_id
        ])
        
    def test_upload_asset_directory_large(self):
        """Test uploading a directory of files with a large number of files"""
        dir_path = "nomad_media_cli/commands"        

        result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", dir_path,
            "--id", self.test_dir_id,
            "--num_files", 16,
            "-r"
        ])
        
        self.assertEqual(result.exit_code, 0)
            
        items = get_total_asset_list(self, self.test_dir_id)
        dir_id = next((item["id"] for item in items if item["name"] == f"{dir_path.split("/")[-1]}/"), None)     
        self.asset_upload_id = dir_id   

        dir_assets = get_total_asset_list(self, dir_id)
            
        check_dir_structure(self, dir_assets, dir_path)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", dir_id
        ])
        
    def test_upload_asset_directory_not_recursive(self):
        """Test directory returns an error"""
        result = self.runner.invoke(cli, [
            "upload-assets", 
            "--source", "nomad_media_cli/tests/test_files",
            "--id", self.test_dir_id,
        ])
        
        self.assertNotEqual(result.exit_code, 0)
            

def get_total_asset_list(self, dir_id):
    items = None
    page_offset = 0
    dir_assets = []

    while True:
        list_assets_result = self.runner.invoke(cli, [
            "list-assets", 
            "--id", dir_id,
            "--page-offset", page_offset, 
            "-r"
        ])

        if list_assets_result.exit_code != 0:
            return

        try:
            output_json = json.loads(list_assets_result.output.replace("False", "false"))
        except Exception as e:
            print(list_assets_result.output)
            self.fail(f"Failed to parse JSON output: {e}")
        items = output_json["items"]
        dir_assets.extend(items)

        if len(items) == 0:
            break

        page_offset += 1
        
        return dir_assets

def check_dir_structure(self, dir_assets, path):
    remote_structure = {}
    path_var = path
    for item in dir_assets:
        path = item["url"].split("::")[1]
        parts = path.split("/")
        current = remote_structure
        for part in parts:
            if part == "":
                continue
            if part not in current:
                current[part] = {}
            current = current[part]
            
    path_dir_found = False
    while True:
        remote_dir_name = list(remote_structure.keys())[0]
        if remote_dir_name == path_var.split("/")[-1]:
            path_dir_found = True
            break
        remote_structure = remote_structure[remote_dir_name]
        
        if remote_structure == {}:
            break
        
    self.assertTrue(path_dir_found)

    local_structure = {}
    for root, dirs, files in os.walk(path_var):
        parts = root.split(os.sep)
        current = local_structure
        for part in parts:
            if part not in current:
                current[part] = {}
            current = current[part]
        for file in files:
            if os.path.getsize(os.path.join(root, file)) == 0:
                continue
            current[file] = {}

    remote_root = list(remote_structure.keys())[0]
    local_root = path_var.replace(os.sep, "/")

    remote_structure = remote_structure[remote_root]
    local_structure = local_structure[local_root]

    remote_structure = dict(sorted(remote_structure.items()))
    local_structure = dict(sorted(local_structure.items()))

    print(json.dumps(remote_structure, indent=4))
    print(json.dumps(local_structure, indent=4))
    self.assertEqual(remote_structure, local_structure)

class TestBucketCommands(TestAssetBase):
    def test_list_buckets(self):
        
        result = self.runner.invoke(cli, ["list-buckets"])
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
        
    def test_set_default_bucket(self):
        
        
        bucket = self.config.get("bucket")
            
        buckets_response = self.runner.invoke(cli, ["list-buckets"])
        buckets = json.loads(buckets_response.output)

        if len(buckets) == 0:
            self.skipTest("No buckets available")

        result = self.runner.invoke(cli, [
            "set-default-bucket",
            "--bucket", buckets[0]])
        
        self.assertEqual(result.exit_code, 0)
        
        with open(self.config_path, "r") as file:
            config = json.load(file)
            new_config_bucket = config.get("bucket")
            
        self.assertEqual(new_config_bucket, buckets[0])
        
        if bucket:
            result = self.runner.invoke(cli, [
                "set-default-bucket",
                "--bucket", bucket])
        
# content metadata tests
class TestAssetAddAssetProperties(TestAssetBase):
    """Tests for adding asset properties"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")
    
    def test_add_asset_properties(self):
        """Test asset properties are added successfully"""
        result = self.runner.invoke(cli, [
            "add-asset-properties", 
            "--id", self.asset_id,
            "--properties", '{"test": "test"}'
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        self.assertEqual(asset_details["customAttributes"]["test"], "test")
        
    def test_add_asset_properties_invalid_json(self):
        """Test invalid JSON returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-properties", 
            "--id", self.asset_id,
            "--properties", "invalid-json"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_add_asset_properties_name(self):
        """Test asset properties are added successfully"""
        result = self.runner.invoke(cli, [
            "add-asset-properties", 
            "--id", self.asset_id,
            "--name", "test",
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        self.assertEqual(asset_details["properties"]["displayName"], "test")
        
    def test_add_asset_properties_date(self):
        """Test asset properties are added successfully"""
        result = self.runner.invoke(cli, [
            "add-asset-properties", 
            "--id", self.asset_id,
            "--date", "2025-01-01T00:00:00Z",
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        self.assertEqual(asset_details["properties"]["displayDate"], "2025-01-01T00:00:00Z")
        
    def test_add_asset_properties_invalid_date(self):
        """Test invalid date returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-properties", 
            "--id", self.asset_id,
            "--date", "invalid-date",
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestAssetAddAssetCollection(TestAssetBase):
    """Tests for adding asset collections"""

    def test_add_asset_collection_by_id(self):
        """Test asset collection is added successfully"""
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--id", self.asset_id,
            "--collection-name", "test-collection"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        collections = asset_details["collections"]
        self.assertTrue(any(collection["description"] == "test-collection" for collection in collections))
        
    def test_add_asset_collection_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--id", "invalid-id",
            "--collection-name", "test-collection"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_add_asset_collection_by_url(self):
        """Test asset collection is added successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--url", url,
            "--collection-name", "test-collection1"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", url
        ])
        
        asset_details = json.loads(asset_details_result.output)
        collections = asset_details["collections"]
        self.assertTrue(any(collection["description"] == "test-collection1" for collection in collections))
        
    def test_add_asset_collection_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--url", "invalid-url",
            "--collection-name", "test-collection"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_add_asset_collection_by_object_key(self):
        """Test asset collection is added successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--object-key", object_key,
            "--collection-name", "test-collection2"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        asset_details = json.loads(asset_details_result.output)
        collections = asset_details["collections"]
        self.assertTrue(any(collection["description"] == "test-collection2" for collection in collections))
        
    def test_add_asset_collection_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--object-key", object_key,
            "--collection-name", "test-collection"
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_add_asset_collection_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--object-key", "invalid-object-key",
            "--collection-name", "test-collection"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_add_asset_collection_by_collection_id(self):
        """Test asset collection is added successfully"""
        collections = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "Collection"
        ])

        collections = json.loads(collections.output)["items"]
        if len(collections) == 0:
            self.skipTest("No collections available")

        collection_id = collections[0]["id"]
        collection_name = collections[0]["title"]

        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--id", self.asset_id,
            "--collection-id", collection_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        collections = asset_details["collections"]
        self.assertTrue(any(collection["description"] == collection_name for collection in collections))
        
    def test_add_asset_collection_by_collection_id_invalid(self):
        """Test invalid collection ID returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--id", self.asset_id,
            "--collection-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestAssetListAssetCollection(TestAssetBase):
    """Tests for listing asset collections"""
    
    def test_list_asset_tag_by_id(self):
        """Test asset collections are returned"""
        result = self.runner.invoke(cli, [
            "list-asset-collections", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_asset_tag_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-collections", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_list_asset_tag_by_url(self):
        """Test asset collections are returned"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "list-asset-collections", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_asset_tag_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-collections", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_list_asset_tag_by_object_key(self):
        """Test asset collections are returned"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "list-asset-collections", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_asset_tag_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "list-asset-collections", 
            "--object-key", object_key
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_list_asset_tag_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-collections", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestAssetRemoveAssetCollection(TestAssetBase):
    """Tests for removing asset collections"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        collections = cls.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "Collection"
        ])

        collections = json.loads(collections.output)["items"]
        if len(collections) == 0:
            cls.skipTest("No collections available")

        cls.collection_id = collections[0]["id"]
        cls.collection_name = collections[0]["title"]

    def test_remove_asset_collection_id(self):
        """Test asset collection is removed successfully"""
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--id", self.asset_id,
            "--collection-id", self.collection_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result = self.runner.invoke(cli, [
            "remove-asset-collection", 
            "--id", self.asset_id,
            "--collection-id", self.collection_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        collections = asset_details["collections"]
        self.assertFalse(self.collection_name in collections)
        
    def test_remove_asset_collection_id_invalid(self):
        """Test invalid collection ID returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-collection", 
            "--id", self.asset_id,
            "--collection-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_remove_asset_collection_by_url(self):
        """Test asset collection is removed successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--url", url,
            "--collection-id", self.collection_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result = self.runner.invoke(cli, [
            "remove-asset-collection", 
            "--url", url,
            "--collection-id", self.collection_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", url
        ])
        
        asset_details = json.loads(asset_details_result.output)
        collections = asset_details["collections"]
        self.assertFalse(self.collection_name in collections)
        
    def test_remove_asset_collection_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-collection", 
            "--url", "invalid-url",
            "--collection-name", "test-collection"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_remove_asset_collection_by_object_key(self):
        """Test asset collection is removed successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--object-key", object_key,
            "--collection-id", self.collection_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result = self.runner.invoke(cli, [
            "remove-asset-collection", 
            "--object-key", object_key,
            "--collection-id", self.collection_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        asset_details = json.loads(asset_details_result.output)
        collections = asset_details["collections"]
        self.assertFalse(self.collection_name in collections)
        
    def test_remove_asset_collection_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "add-asset-collection", 
            "--object-key", object_key,
            "--collection-id", self.collection_id
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_remove_asset_collection_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-collection", 
            "--object-key", "invalid-object-key",
            "--collection-name", "test-collection"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestAssetAddAssetTag(TestAssetBase):
    """Tests for adding asset tags"""

    def test_add_asset_tag_by_id(self):
        """Test asset tag is added successfully"""
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--id", self.asset_id,
            "--tag-name", "test-tag"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        tags = asset_details["tags"]
        self.assertTrue(any(tag["description"] == "test-tag" for tag in tags))
        
    def test_add_asset_tag_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--id", "invalid-id",
            "--tag-name", "test-tag"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_add_asset_tag_by_url(self):
        """Test asset tag is added successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--url", url,
            "--tag-name", "test-tag1"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", url
        ])
        
        asset_details = json.loads(asset_details_result.output)
        tags = asset_details["tags"]
        self.assertTrue(any(tag["description"] == "test-tag1" for tag in tags))
        
    def test_add_asset_tag_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--url", "invalid-url",
            "--tag-name", "test-tag"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_add_asset_tag_by_object_key(self):
        """Test asset tag is added successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--object-key", object_key,
            "--tag-name", "test-tag2"
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        asset_details = json.loads(asset_details_result.output)
        tags = asset_details["tags"]
        self.assertTrue(any(tag["description"] == "test-tag2" for tag in tags))
        
    def test_add_asset_tag_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--object-key", object_key,
            "--tag-name", "test-tag"
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_add_asset_tag_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--object-key", "invalid-object-key",
            "--tag-name", "test-tag"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_add_asset_tag_by_tag_id(self):
        """Test asset tag is added successfully"""
        tags = self.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "Tag"
        ])

        tags = json.loads(tags.output)["items"]
        if len(tags) == 0:
            self.skipTest("No tags available")

        tag_id = tags[0]["id"]
        tag_name = tags[0]["title"]

        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--id", self.asset_id,
            "--tag-id", tag_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        tags = asset_details["tags"]
        self.assertTrue(any(tag["description"] == tag_name for tag in tags))

    def test_add_asset_tag_by_tag_id_invalid(self):
        """Test invalid tag ID returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--id", self.asset_id,
            "--tag-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestAssetListAssetTag(TestAssetBase):
    """Tests for listing asset tags"""

    def test_list_asset_tag_by_id(self):
        """Test asset tags are returned"""
        result = self.runner.invoke(cli, [
            "list-asset-tags", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_asset_tag_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-tags", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_list_asset_tag_by_url(self):
        """Test asset tags are returned"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "list-asset-tags", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_asset_tag_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-tags", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_list_asset_tag_by_object_key(self):
        """Test asset tags are returned"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "list-asset-tags", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_asset_tag_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "list-asset-tags", 
            "--object-key", object_key
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_list_asset_tag_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-tags", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestAssetRemoveAssetTag(TestAssetBase):
    """Tests for removing asset tags"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        tags = cls.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "Tag"
        ])

        tags = json.loads(tags.output)["items"]
        if len(tags) == 0:
            cls.skipTest("No tags available")

        cls.tag_id = tags[0]["id"]
        cls.tag_name = tags[0]["title"]
        
        tag_result = cls.runner.invoke(cli, [
            "add-asset-tag", 
            "--id", cls.asset_id,
            "--tag-id", cls.tag_id
        ])
        
        if tag_result.exit_code != 0:
            cls.skipTest("Failed to add tag")

    def test_remove_asset_tag_id(self):
        """Test asset tag is removed successfully"""
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--id", self.asset_id,
            "--tag-id", self.tag_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result = self.runner.invoke(cli, [
            "remove-asset-tag", 
            "--id", self.asset_id,
            "--tag-id", self.tag_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        tags = asset_details["tags"]
        self.assertFalse(self.tag_name in tags)
        
    def test_remove_asset_tag_id_invalid(self):
        """Test invalid tag ID returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-tag", 
            "--id", self.asset_id,
            "--tag-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_remove_asset_tag_by_url(self):
        """Test asset tag is removed successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--url", url,
            "--tag-id", self.tag_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result = self.runner.invoke(cli, [
            "remove-asset-tag", 
            "--url", url,
            "--tag-id", self.tag_id
        ])
        
        self.assertEqual(result.exit_code, 0)

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", url
        ])

        asset_details = json.loads(asset_details_result.output)
        tags = asset_details["tags"]
        self.assertFalse(self.tag_name in tags)

    def test_remove_asset_tag_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-tag", 
            "--url", "invalid-url",
            "--tag-id", self.tag_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_remove_asset_tag_by_object_key(self):
        """Test asset tag is removed successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--object-key", object_key,
            "--tag-id", self.tag_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        result = self.runner.invoke(cli, [
            "remove-asset-tag", 
            "--object-key", object_key,
            "--tag-id", self.tag_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        asset_details = json.loads(asset_details_result.output)
        tags = asset_details["tags"]
        self.assertFalse(self.tag_name in tags)

    def test_remove_asset_tag_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "add-asset-tag", 
            "--object-key", object_key,
            "--tag-id", self.tag_id
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_remove_asset_tag_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-tag", 
            "--object-key", "invalid-object-key",
            "--tag-id", self.tag_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestAssetAddRelatedContent(TestAssetBase):
    """Tests for adding related content"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        series_result = cls.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "Series"
        ])

        countries = json.loads(series_result.output)["items"]
        if len(countries) == 0:
            cls.skipTest("Content definition not available")

        cls.series_id = countries[0]["id"]
        cls.series_name = countries[0]["title"]

    def test_add_related_content_by_id(self):
        """Test related content is added successfully"""
        result = self.runner.invoke(cli, [
            "add-asset-related-content", 
            "--id", self.asset_id,
            "--related-content-id", self.series_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        related_contents = asset_details["relatedContent"]
        self.assertTrue(any(content["id"] == self.series_id for content in related_contents))
        
    def test_add_related_content_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-related-content", 
            "--id", "invalid-id",
            "--related-content-id", self.series_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_add_related_content_by_url(self):
        """Test related content is added successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "add-asset-related-content", 
            "--url", url,
            "--related-content-id", self.series_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", url
        ])
        
        asset_details = json.loads(asset_details_result.output)
        related_contents = asset_details["relatedContent"]

        self.assertTrue(any(content["id"] == self.series_id for content in related_contents))

    def test_add_related_content_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-related-content", 
            "--url", "invalid-url",
            "--related-content-id", self.series_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_add_related_content_by_object_key(self):
        """Test related content is added successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "add-asset-related-content", 
            "--object-key", object_key,
            "--related-content-id", self.series_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        asset_details = json.loads(asset_details_result.output)
        related_contents = asset_details["relatedContent"]
        self.assertTrue(any(content["id"] == self.series_id for content in related_contents))

    def test_add_related_content_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]

        result = self.runner.invoke(cli, [
            "add-asset-related-content", 
            "--object-key", object_key,
            "--related-content-id", self.series_id
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_add_related_content_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-related-content", 
            "--object-key", "invalid-object-key",
            "--related-content-id", self.series_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_add_related_content_by_content_id_invalid(self):
        """Test invalid content ID returns an error"""
        result = self.runner.invoke(cli, [
            "add-asset-related-content", 
            "--id", self.asset_id,
            "--related-content-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestAssetListRelatedContent(TestAssetBase):
    """Tests for listing related content"""

    def test_list_related_content_by_id(self):
        """Test related content is returned"""
        result = self.runner.invoke(cli, [
            "list-asset-related-contents", 
            "--id", self.asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_related_content_by_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-related-contents", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_list_related_content_by_url(self):
        """Test related content is returned"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "list-asset-related-contents", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")

    def test_list_related_content_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-related-contents", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_list_related_content_by_object_key(self):
        """Test related content is returned"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "list-asset-related-contents", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        try:
            output_json = json.loads(result.output)
            self.assertTrue(isinstance(output_json, list))
        except json.JSONDecodeError:
            self.fail("Output is not valid JSON")
            
    def test_list_related_content_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "list-asset-related-contents", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_list_related_content_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "list-asset-related-contents", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
class TestAssetRemoveRelatedContent(TestAssetBase):
    """Tests for removing related content"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        series_result = cls.runner.invoke(cli, [
            "get-content-definition-contents",
            "--name", "Series"
        ])

        countries = json.loads(series_result.output)["items"]
        if len(countries) == 0:
            cls.skipTest("Content definition not available")

        cls.series_id = countries[0]["id"]
        cls.series_name = countries[0]["title"]
        
        related_content_result = cls.runner.invoke(cli, [
            "add-asset-related-content", 
            "--id", cls.asset_id,
            "--related-content-id", cls.series_id
        ])
        
        if related_content_result.exit_code != 0:
            cls.skipTest("Failed to add related content")

    def test_remove_related_content_id(self):
        """Test related content is removed successfully"""
        result = self.runner.invoke(cli, [
            "remove-asset-related-content", 
            "--id", self.asset_id,
            "--related-content-id", self.series_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        related_contents = asset_details["relatedContent"]
        self.assertFalse(self.series_name in related_contents)
        
    def test_remove_related_content_id_invalid(self):
        """Test invalid ID returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-related-content", 
            "--id", self.asset_id,
            "--related-content-id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_remove_related_content_by_url(self):
        """Test related content is removed successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "remove-asset-related-content", 
            "--url", url,
            "--related-content-id", self.series_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", url
        ])
        
        asset_details = json.loads(asset_details_result.output)
        related_contents = asset_details["relatedContent"]
        
        self.assertFalse(self.series_name in related_contents)
        
    def test_remove_related_content_by_url_invalid(self):
        """Test invalid URL returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-related-content", 
            "--url", "invalid-url",
            "--related-content-id", self.series_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_remove_related_content_by_object_key(self):
        """Test related content is removed successfully"""
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "remove-asset-related-content", 
            "--object-key", object_key,
            "--related-content-id", self.series_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        asset_details = json.loads(asset_details_result.output)
        related_contents = asset_details["relatedContent"]
        
        self.assertFalse(self.series_name in related_contents)
        
    def test_remove_related_content_by_object_key_no_bucket(self):
        """Test missing bucket returns an error"""
        

        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
            
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", self.asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "remove-asset-related-content", 
            "--object-key", object_key,
            "--related-content-id", self.series_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)
        
    def test_remove_related_content_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "remove-asset-related-content", 
            "--object-key", "invalid-object-key",
            "--related-content-id", self.series_id
        ])
        
        self.assertNotEqual(result.exit_code, 0)

class TestDeleteAsset(TestAssetBase):
    """Tests for deleting assets"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        if cls.config["apiType"] != "admin":
            raise unittest.SkipTest("API type is not admin")
        
    def test_delete_asset_by_id(self):
        """Test asset is deleted successfully"""
        result = self.runner.invoke(cli, [
            "upload-assets",
            "--source", "requirements.txt",
            "--id", self.test_dir_id
        ])

        dir_content_list = get_total_asset_list(self, self.test_dir_id)
        asset_id = next((item for item in dir_content_list if item["name"] == "requirements.txt"), None)["id"] 

        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--id", asset_id
        ])
        
        self.assertEqual(result.exit_code, 0)
        time.sleep(5)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", asset_id
        ])
        
        self.assertNotEqual(asset_details_result.exit_code, 0)
        
        self.runner.invoke(cli, [
            "delete-asset", 
            "--id", asset_id
        ])

    def test_delete_asset_by_id_invalid(self):
        """Test invalid ID returns an error"""    
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--id", "invalid-id"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

    def test_delete_asset_by_url(self):
        """Test asset is deleted successfully"""
        result = self.runner.invoke(cli, [
            "upload-assets",
            "--source", "requirements.txt",
            "--id", self.test_dir_id
        ])

        dir_content_list = get_total_asset_list(self, self.test_dir_id)
        asset_id = next((item for item in dir_content_list if item["name"] == "requirements.txt"), None)["id"]     

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", asset_id
        ])
        
        asset_details = json.loads(asset_details_result.output)

        url = asset_details["properties"]["url"]
        
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--url", url
        ])
        
        self.assertEqual(result.exit_code, 0)
        time.sleep(5)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--url", url
        ])
        
        self.assertNotEqual(asset_details_result.exit_code, 0)

    def test_delete_asset_by_url_invalid(self):
        """Test invalid URL returns an error"""            
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--url", "invalid-url"
        ])
        
        self.assertNotEqual(result.exit_code, 0)


    def test_delete_asset_by_object_key(self):
        """Test asset is deleted successfully"""
        result = self.runner.invoke(cli, [
            "upload-assets",
            "--source", "publish.bat",
            "--id", self.test_dir_id
        ])

        dir_content_list = get_total_asset_list(self, self.test_dir_id)
        asset_id = next((item for item in dir_content_list if item["name"] == "publish.bat"), None)["id"]        

        time.sleep(5)

        asset_details_result = self.runner.invoke(cli, [
                "get-asset-details", 
                "--id", asset_id
            ])
    
        asset_details = json.loads(asset_details_result.output)      

        object_key = asset_details["properties"]["displayPath"]
        
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--object-key", object_key
        ])
        
        self.assertEqual(result.exit_code, 0)
        time.sleep(3)
        
        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--object-key", object_key
        ])
        
        self.assertNotEqual(asset_details_result.exit_code, 0)

    def test_delete_asset_by_object_key_no_bucket(self):
        
        
        bucket = self.config.get("bucket")
        if bucket:
            self.skipTest("Default bucket set")
        
        result = self.runner.invoke(cli, [
            "upload-assets",
            "--source", "requirements.txt",
            "--id", self.test_dir_id
        ])

        asset_id = result.output.replace('"', "").strip()
        
        time.sleep(3)

        asset_details_result = self.runner.invoke(cli, [
            "get-asset-details", 
            "--id", asset_id
        ])

        asset_details = json.loads(asset_details_result.output)
        object_key = asset_details["properties"]["displayPath"]
        
        time.sleep(3)

        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--object-key", object_key
        ])

        self.assertNotEqual(result.exit_code, 0)

    def test_delete_asset_by_object_key_invalid(self):
        """Test invalid object key returns an error"""
        result = self.runner.invoke(cli, [
            "delete-asset", 
            "--object-key", "invalid-object-key"
        ])
        
        self.assertNotEqual(result.exit_code, 0)

if __name__ == "__main__":
    unittest.main()
        
