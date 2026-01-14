#!/usr/bin/env python3
import argparse
import getpass
import sys
import os

# 直接使用绝对导入，因为当包被正确安装后，Python会自动将包的安装目录添加到sys.path中
from pyipatool.api import API
from pyipatool.models import AuthError

def main():
    parser = argparse.ArgumentParser(description='ipatool - 用于从 iOS App Store 下载 ipa 文件的命令行工具')
    
    # 全局参数
    parser.add_argument('--data-dir', help='数据目录路径（默认：包安装目录下的data文件夹）')
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # auth 命令
    auth_parser = subparsers.add_parser('auth', help='Apple ID 认证相关命令')
    auth_subparsers = auth_parser.add_subparsers(dest='auth_command', help='认证子命令')
    
    # auth login 命令
    login_parser = auth_subparsers.add_parser('login', help='登录 Apple ID')
    login_parser.add_argument('-e', '--email', required=True, help='Apple ID 邮箱')
    login_parser.add_argument('-p', '--password', help='Apple ID 密码')
    login_parser.add_argument('--auth-code', help='2FA 验证码')
    
    # auth revoke 命令
    revoke_parser = auth_subparsers.add_parser('revoke', help='撤销 App Store 凭证')
    
    # auth info 命令
    info_parser = auth_subparsers.add_parser('info', help='显示当前登录信息')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索 iOS 应用')
    search_parser.add_argument('term', help='搜索关键词')
    search_parser.add_argument('--limit', type=int, default=5, help='结果数量限制（默认：5）')
    
    # list-versions 命令
    list_versions_parser = subparsers.add_parser('list-versions', help='列出应用的所有版本')
    list_versions_parser.add_argument('-i', '--app-id', help='应用 ID')
    list_versions_parser.add_argument('-b', '--bundle-id', help='应用 Bundle ID')
    
    # download 命令
    download_parser = subparsers.add_parser('download', help='下载应用 IPA 文件')
    download_parser.add_argument('-i', '--app-id', help='应用 ID')
    download_parser.add_argument('-b', '--bundle-id', help='应用 Bundle ID')
    download_parser.add_argument('--output', default='', help='输出路径（默认：当前目录）')
    download_parser.add_argument('--version-id', default='', help='特定版本的外部标识符')
    
    # lookup 命令
    lookup_parser = subparsers.add_parser('lookup', help='通过 Bundle ID 查询应用信息')
    lookup_parser.add_argument('-b', '--bundle-id', required=True, help='应用 Bundle ID')

    # get-version-metadata 命令
    get_version_metadata_parser = subparsers.add_parser('get-version-metadata', help='获取指定版本的应用元数据')
    get_version_metadata_parser.add_argument('-i', '--app-id', help='应用 ID')
    get_version_metadata_parser.add_argument('-b', '--bundle-id', help='应用 Bundle ID')
    get_version_metadata_parser.add_argument('--version-id', required=True, help='特定版本的外部标识符')

    args = parser.parse_args()
    
    api = API(data_dir=args.data_dir)
    
    if args.command == 'auth':
        if args.auth_command == 'login':
            # 处理密码输入
            password = args.password
            if not password:
                password = getpass.getpass('Enter password: ')
            
            # 处理登录，支持2FA重试
            auth_code = args.auth_code or ""
            last_error = None
            
            for attempt in range(2):
                try:
                    account = api.login(args.email, password, auth_code)
                    print(f"Login successful! Welcome, {account.name}")
                    print(f"Email: {account.email}")
                    break
                except AuthError as e:
                    print(f"Login failed: {str(e)}")
                    break
        elif args.auth_command == 'revoke':
            api.logout()
            api.auth.cookie_jar.clear()
            print("Successfully revoked credentials and cleared cookies")
        elif args.auth_command == 'info':
            account = api.get_account_info()
            if account:
                print("Current login info:")
                print(f"Name: {account.name}")
                print(f"Email: {account.email}")
            else:
                print("Not logged in")
        else:
            auth_parser.print_help()
    elif args.command == 'search':
        try:
            result = api.search(args.term, args.limit)
            print(f"Search results for '{args.term}' (found {result.count} apps):")
            print("-" * 80)
            print(f"{'ID':<15} {'Bundle ID':<40} {'Name':<30} {'Version':<10} {'Price':<10}")
            print("-" * 80)
            for app in result.results:
                print(f"{app.id:<15} {app.bundle_id:<40} {app.name:<30} {app.version:<10} {app.price:<10}")
            print("-" * 80)
        except AuthError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
    elif args.command == 'list-versions':
        try:
            if not args.app_id and not args.bundle_id:
                print("Error: Either --app-id or --bundle-id must be specified")
                list_versions_parser.print_help()
                return
            
            result = api.list_versions(args.app_id, args.bundle_id)
            print("Version identifiers:")
            print("-" * 80)
            if result.external_version_identifiers:
                # 用空格分隔显示版本ID，每行显示多个
                version_ids_str = " ".join(result.external_version_identifiers)
                print(version_ids_str)
            else:
                print("No versions found")
            print("-" * 80)
            print(f"Total versions: {len(result.external_version_identifiers)}")
        except AuthError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
    elif args.command == 'download':
        try:
            if not args.app_id and not args.bundle_id:
                print("Error: Either --app-id or --bundle-id must be specified")
                download_parser.print_help()
                return
            
            destination = api.download(
                app_id=args.app_id,
                bundle_id=args.bundle_id,
                output_path=args.output,
                external_version_id=args.version_id
            )
            print(f"Download completed successfully!")
            print(f"IPA file saved to: {destination}")
        except AuthError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
    elif args.command == 'lookup':
        try:
            result = api.lookup(args.bundle_id)
            print("App information:")
            print("-" * 80)
            print(f"Name: {result.app.name}")
            print(f"Bundle ID: {result.app.bundle_id}")
            print(f"App ID: {result.app.id}")
            print(f"Version: {result.app.version}")
            print("-" * 80)
        except AuthError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
    elif args.command == 'get-version-metadata':
        try:
            if not args.app_id and not args.bundle_id:
                print("Error: Either --app-id or --bundle-id must be specified")
                get_version_metadata_parser.print_help()
                return
            
            result = api.get_version_metadata(
                app_id=args.app_id,
                bundle_id=args.bundle_id,
                external_version_id=args.version_id
            )
            print("Version metadata:")
            print("-" * 80)
            print(f"App ID: {result.id}")
            print(f"Name: {result.name}")
            print(f"Version: {result.version}")
            print("-" * 80)
        except AuthError as e:
            print(f"Error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
    else:
        parser.print_help()

def cli():
    """Command-line interface entry point"""
    main()

if __name__ == '__main__':
    main()