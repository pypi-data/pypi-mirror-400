import os

class DBSettings:
    def __init__(self, 
                 env_url:str="BOLT_URL",
                 env_user:str="BOLT_USER", 
                 env_password:str="BOLT_PASSWORD"):
        """ Initialize database settings from environment variables.
        :param env_url: Environment variable for the database URL.
        :param env_user: Environment variable for the database user.    
        :param env_password: Environment variable for the database password.
        """
        self.url:str = os.getenv(env_url)
        self.user:str = os.getenv(env_user)
        self.password:str = os.getenv(env_password)
        self.num_retries:int = 5
        self.backoff_seconds:float = 2
        # Kill pooled conns before GCP/LB idle timeout (~10m) can drop them.
        self.max_connection_lifetime:int = 540   # 9 minutes (in seconds)
        # Proactively test long-idle conns before reuse to avoid "first write fails".
        self.liveness_check_timeout:int = 480    # 8 minutes (in seconds)
