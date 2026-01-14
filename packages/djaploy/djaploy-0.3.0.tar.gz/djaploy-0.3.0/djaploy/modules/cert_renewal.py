"""
Certificate renewal module for djaploy

Configures automatic certificate renewal on servers using systemd timers.
Supports both certbot-based renewals and certificate sync from 1Password.
"""

from djaploy.modules.base import BaseModule
from pyinfra.operations import systemd, files, server, apt


class CertRenewalModule(BaseModule):
    """
    Automatic SSL certificate renewal using systemd timers

    This module can operate in two modes:
    1. Primary renewal server: Runs certbot to renew certificates locally
    2. Secondary servers: Syncs certificates from 1Password

    Configuration in HostConfig:
        primary_renewal_server: bool - If True, this server will run certbot renewals
        renewal_email: str - Email for Let's Encrypt (optional, uses project config by default)
        renewal_schedule: str - systemd timer schedule (default: weekly Sunday 3 AM)
        sync_schedule: str - Certificate sync schedule (default: daily 4 AM)
    """

    name = "cert_renewal"
    description = "Configures automatic certificate renewal via systemd timers"

    def configure_server(self, host_data, project_config):
        """Install renewal service and timer"""

        is_primary = host_data.get('primary_renewal_server', True)
        app_user = host_data.get('app_user', project_config.app_user)
        project_name = host_data.get('project_name', project_config.project_name)
        project_dir = f"/home/{app_user}/{project_name}"
        environment = host_data.get('environment', 'production')

        # Get configuration
        renewal_email = host_data.get('renewal_email', getattr(project_config, 'ssl_email', None))
        op_account = getattr(project_config, 'op_account', None)
        renewal_schedule = host_data.get('renewal_schedule', 'Sun *-*-* 03:00:00')
        sync_schedule = host_data.get('sync_schedule', '*-*-* 04:00:00')

        if is_primary:
            self._configure_primary_renewal(
                app_user=app_user,
                project_dir=project_dir,
                project_name=project_name,
                environment=environment,
                renewal_email=renewal_email,
                op_account=op_account,
                renewal_schedule=renewal_schedule,
            )
        else:
            self._configure_secondary_sync(
                app_user=app_user,
                project_dir=project_dir,
                project_name=project_name,
                environment=environment,
                op_account=op_account,
                sync_schedule=sync_schedule,
            )

    def _configure_primary_renewal(
        self,
        app_user: str,
        project_dir: str,
        project_name: str,
        environment: str,
        renewal_email: str,
        op_account: str,
        renewal_schedule: str,
    ):
        """Configure primary renewal server with certbot"""

        # Install certbot
        apt.packages(
            name="Install certbot",
            packages=["certbot"],
            update=True,
            _sudo=True,
        )

        # Install certbot-dns-bunny if using BunnyDnsCertificate
        server.shell(
            name="Install certbot-dns-bunny plugin",
            commands=["pip3 install certbot-dns-bunny"],
            _sudo=True,
        )

        if not renewal_email:
            raise ValueError(
                "renewal_email is required for primary renewal server. "
                "Set it in HostConfig or project_config.ssl_email"
            )

        # Build environment variables
        env_vars = [
            f"DJANGO_SETTINGS_MODULE={project_name}.settings.{environment}",
        ]
        if op_account:
            env_vars.append(f"OP_ACCOUNT={op_account}")

        env_string = "\n".join([f'Environment="{var}"' for var in env_vars])

        # Create renewal + sync service
        service_content = f"""[Unit]
Description=Renew SSL Certificates
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User={app_user}
WorkingDirectory={project_dir}/djangoroot
{env_string}
# First renew certificates
ExecStart=/usr/local/bin/poetry run python manage.py update_certs \\
    --email {renewal_email} \\
    --days-before-expiry 30
# Then sync to all servers (if configured)
ExecStartPost=-/usr/local/bin/poetry run python manage.py sync_certs --env {environment}
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ssl-renew

[Install]
WantedBy=multi-user.target
"""

        files.put(
            name="Upload certificate renewal service",
            src=None,
            dest="/etc/systemd/system/ssl-renew.service",
            user="root",
            group="root",
            mode="644",
            create_remote_dir=False,
            _sudo=True,
        )
        files.line(
            name="Write renewal service content",
            path="/etc/systemd/system/ssl-renew.service",
            line=service_content,
            replace=r".*",
            _sudo=True,
        )

        # Create renewal timer
        timer_content = f"""[Unit]
Description=Weekly SSL Certificate Renewal
Requires=ssl-renew.service

[Timer]
OnCalendar={renewal_schedule}
Persistent=true
RandomizedDelaySec=1h

[Install]
WantedBy=timers.target
"""

        files.put(
            name="Upload certificate renewal timer",
            src=None,
            dest="/etc/systemd/system/ssl-renew.timer",
            user="root",
            group="root",
            mode="644",
            create_remote_dir=False,
            _sudo=True,
        )
        files.line(
            name="Write renewal timer content",
            path="/etc/systemd/system/ssl-renew.timer",
            line=timer_content,
            replace=r".*",
            _sudo=True,
        )

        # Reload systemd and enable timer
        systemd.daemon_reload(
            name="Reload systemd daemon",
            _sudo=True,
        )

        systemd.service(
            name="Enable and start renewal timer",
            service="ssl-renew.timer",
            running=True,
            enabled=True,
            restarted=False,
            _sudo=True,
        )

        print(f"✓ Configured primary renewal server with schedule: {renewal_schedule}")
        print(f"  - Service: ssl-renew.service")
        print(f"  - Timer: ssl-renew.timer")
        print(f"  - Check status: systemctl status ssl-renew.timer")
        print(f"  - View logs: journalctl -u ssl-renew.service")
        print(f"  - Test renewal: systemctl start ssl-renew.service")

    def _configure_secondary_sync(
        self,
        app_user: str,
        project_dir: str,
        project_name: str,
        environment: str,
        op_account: str,
        sync_schedule: str,
    ):
        """Configure secondary server to sync certificates from 1Password"""

        # Build environment variables
        env_vars = [
            f"DJANGO_SETTINGS_MODULE={project_name}.settings.{environment}",
        ]
        if op_account:
            env_vars.append(f"OP_ACCOUNT={op_account}")

        env_string = "\n".join([f'Environment="{var}"' for var in env_vars])

        # Create sync service
        service_content = f"""[Unit]
Description=Sync SSL Certificates from 1Password
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User={app_user}
WorkingDirectory={project_dir}/djangoroot
{env_string}
ExecStart=/usr/local/bin/poetry run python manage.py sync_certs --env {environment}
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ssl-sync

[Install]
WantedBy=multi-user.target
"""

        files.put(
            name="Upload certificate sync service",
            src=None,
            dest="/etc/systemd/system/ssl-sync.service",
            user="root",
            group="root",
            mode="644",
            create_remote_dir=False,
            _sudo=True,
        )
        files.line(
            name="Write sync service content",
            path="/etc/systemd/system/ssl-sync.service",
            line=service_content,
            replace=r".*",
            _sudo=True,
        )

        # Create sync timer
        timer_content = f"""[Unit]
Description=Daily SSL Certificate Sync
Requires=ssl-sync.service

[Timer]
OnCalendar={sync_schedule}
Persistent=true
RandomizedDelaySec=30min

[Install]
WantedBy=timers.target
"""

        files.put(
            name="Upload certificate sync timer",
            src=None,
            dest="/etc/systemd/system/ssl-sync.timer",
            user="root",
            group="root",
            mode="644",
            create_remote_dir=False,
            _sudo=True,
        )
        files.line(
            name="Write sync timer content",
            path="/etc/systemd/system/ssl-sync.timer",
            line=timer_content,
            replace=r".*",
            _sudo=True,
        )

        # Reload systemd and enable timer
        systemd.daemon_reload(
            name="Reload systemd daemon",
            _sudo=True,
        )

        systemd.service(
            name="Enable and start sync timer",
            service="ssl-sync.timer",
            running=True,
            enabled=True,
            restarted=False,
            _sudo=True,
        )

        print(f"✓ Configured secondary server with sync schedule: {sync_schedule}")
        print(f"  - Service: ssl-sync.service")
        print(f"  - Timer: ssl-sync.timer")
        print(f"  - Check status: systemctl status ssl-sync.timer")
        print(f"  - View logs: journalctl -u ssl-sync.service")
        print(f"  - Test sync: systemctl start ssl-sync.service")


Module = CertRenewalModule
