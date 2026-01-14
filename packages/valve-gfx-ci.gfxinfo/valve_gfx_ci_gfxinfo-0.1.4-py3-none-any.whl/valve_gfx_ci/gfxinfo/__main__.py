import argparse
import sys
import json

from . import find_gpu, VulkanInfo, PCIDevice, find_gpu_from_pciid, check_db


def output_gpu_info(gpu, show_vk_info=True):
    gfxinfo = {
        'tags': list(gpu.tags),
        'structured_tags': gpu.structured_tags,
        'base_name': gpu.base_name,
    }
    if show_vk_info:
        if info := VulkanInfo.construct():
            gfxinfo["vk:vram_size_gib"] = "%.2f" % info.VRAM_heap.GiB_size
            gfxinfo["vk:gtt_size_gib"] = "%.2f" % info.GTT_heap.GiB_size
            if info.mesa_version is not None:
                gfxinfo["mesa:version"] = info.mesa_version
            if info.mesa_git_version is not None:
                gfxinfo["mesa:git:version"] = info.mesa_git_version
            if info.device_name is not None:
                gfxinfo["vk:device:name"] = info.device_name
            if info.device_type is not None:
                gfxinfo["vk:device:type"] = info.device_type.name
            if info.api_version is not None:
                gfxinfo["vk:api:version"] = info.api_version
            if info.driver_name is not None:
                gfxinfo["vk:driver:name"] = info.driver_name
            if info.driver_info is not None:
                gfxinfo["vk:driver:info"] = info.driver_info
    json.dump(gfxinfo, sys.stdout)
    sys.stdout.write("\n")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(prog='GFXInfo')
    parser.add_argument("-p", '--pciid')
    parser.add_argument('--check-db', action="store_true")
    args = parser.parse_args()

    if args.check_db:
        ret = check_db()
        if ret:
            print("All databases passed their checks!")
        else:
            print("ERROR: At least one database is invalid")
        sys.exit(0 if ret else 1)

    elif args.pciid:
        pciid = PCIDevice.from_str(args.pciid)
        if gpu := find_gpu_from_pciid(pciid):
            output_gpu_info(gpu, show_vk_info=False)
        else:
            json.dump({"error": f"No GPU found matching the PCIID '{args.pciid}'"}, sys.stdout)
            sys.exit(1)

    else:
        if gpu := find_gpu():
            output_gpu_info(gpu)
        else:
            json.dump({"error": "No suitable GPU found"}, sys.stdout)
            sys.exit(1)


if __name__ == '__main__':
    main()
