import random
import string
from datetime import datetime

from apis.models import Product, MediaFile
from apis.serializer import ProductSerializer, MediaFileSerializer
from uiflo import settings


def random_string(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def uploadtos3(filename, body):
    import boto3
    key = "products/"+filename+".html"
    key = key.replace(" ", "-")

    client = boto3.client('s3',
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name='ap-south-1'
    )
    response = client.put_object(
        Bucket='www.flomo.design',
        Body=body,
        Key=key,
        ContentType="text/html",
        ACL="public-read"
    )
    fetchfroms3(key)


def fetchfroms3(filename):
    import boto3
    key = "sitemap.xml"

    client = boto3.client('s3',
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name='ap-south-1'
    )
    response = client.get_object(
        Bucket='www.flomo.design',
        Key=key
    )
    sitemap = response.get('Body').read()
    sitemap = str(sitemap) + """ 
    <url>
        <loc>https://www.flomo.design/{key}</loc>
        <lastmod>{date}</lastmod>
        <priority>0.5</priority>
    </url>
    """.format(key=filename, date=datetime.utcnow().isoformat()[:19]+"+00:00")
    sitemap = sitemap.replace("b'", "")
    sitemap = sitemap.replace("'", "")
    sitemap = sitemap.replace("</urlset>", "")
    sitemap = sitemap.replace(r"\xef\xbb\xbf", "")
    sitemap = sitemap.replace(r"\n", "")
    sitemap = sitemap.replace(r"\t", "")
    sitemap = sitemap.replace(r"\r", "")
    sitemap = sitemap + "</urlset>"
    print(sitemap)
    print(type(sitemap))
    response = client.put_object(
        Bucket='www.flomo.design',
        Body=sitemap,
        Key="sitemap.xml",
        ContentType="text/xml",
        ACL="public-read"
    )


def generate_product_page(id="1ef7139b-e8ca-4af2-8984-cddf6230f644"):
    from apis.common.productTemplate import templatePage
    product = Product.objects.get(uuid=id)
    product = ProductSerializer(product).data
    title = product['sub_flow'] if product['sub_flow'] else product['flow']
    title = title + " on " + product['product']
    content = ""
    print(product['media'])
    print(type(product['media']))
    files = MediaFile.objects.filter(uuid__in=product['media'], media_type="video")[0]
    video = MediaFileSerializer(files).data
    print(video)
    time = 0
    for e in video['annotations'][0]:
        content = content + """
        <h3> {0} </h3>
        <p> {1} </p>
        """.format(e['heading'], e['description'])
        time = e['time']
    print(content)
    print(time)
    time = "PT" + str(int(time/60)) + "M" + str(int(time % 60)) + "S"
    print(time)
    date = str(video['created_at'])[:10]
    file = templatePage.format(title=title, content=content, date=date, duration=time, thumbnail=product['thumbnail'],
                             category=product['category'], device=product['device'],uuid=id)
    file = file.replace("<openjson>", "{")
    file = file.replace("</openjson>", "}")
    file = file.replace("</openjson>", "}")
    print(file)
    uploadtos3(title, file)
    return file
