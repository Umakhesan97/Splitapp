import redis

# Create a Redis client instance
redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

# Set a key-value pair in the Redis database
redis_client.set('key', 'value')

# Retrieve the value of the 'key' from the Redis database
value = redis_client.get('key')

# Print the value
print(value)