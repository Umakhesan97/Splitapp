import redis

# Connect to the Redis server
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# Check if the server is reachable
try:
    response = redis_client.ping()
    print(f"Redis server is reachable: {response}")
except redis.exceptions.ConnectionError:
    print("Unable to connect to the Redis server.")
