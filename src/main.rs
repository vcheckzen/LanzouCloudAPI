use std::{env, fmt};
use std::error::Error;
use std::fmt::{Debug, Display, Formatter};

use regex::Regex;
use reqwest::header::{ACCEPT_LANGUAGE, CONTENT_TYPE, HeaderMap, HeaderValue, LOCATION, REFERER, USER_AGENT};
use serde::Deserialize;
use url::form_urlencoded::Serializer;

const ORIGIN: &str = "https://lanzoux.com";

const USER_AGENTS: (&str, &str) = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0; Pixel 2 Build/OPD3.170816.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Mobile Safari/537.36"
);

enum ClientType {
    PC,
    MOBILE,
}

#[derive(Clone)]
struct FileMeta {
    id: String,
    pwd: String,
}

#[derive(Deserialize, Debug)]
struct FakeResponse {
    dom: String,
    url: String,
}

#[derive(Debug)]
struct RegexExtractError(String);

impl Display for RegexExtractError {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        write!(f, "{:?}", self)
    }
}

impl Error for RegexExtractError {}

type Response<T> = Result<T, Box<dyn Error>>;

macro_rules! gen_default_headers {
    ($client_type:expr) => {
       {
           let mut headers = HeaderMap::new();
           headers.insert(ACCEPT_LANGUAGE, "zh-CN,zh;q=0.9,en;q=0.8".parse().unwrap());
           headers.insert(REFERER, ORIGIN.parse().unwrap());
           headers.insert(USER_AGENT, match $client_type {
                ClientType::PC => USER_AGENTS.0,
                ClientType::MOBILE => USER_AGENTS.1,
            }.parse().unwrap());
           headers
       }
    };
}

macro_rules! get_text {
    ($client:expr, $url:expr) => {
        $client.get($url)
            .send()
            .await?
            .text()
            .await?
    };
}

fn extract_unique_capture<'a>(text: &'a str, pattern: &str) -> Response<&'a str> {
    Ok(Regex::new(pattern)?
        .captures(text)
        .ok_or(RegexExtractError(format!("`{}` and `{}` don't match", text, pattern)))?
        .get(1)
        .ok_or(RegexExtractError(format!("`no capture of `{}` in `{}`", pattern, text)))?
        .as_str())
}

fn parse_params(text: &str) -> Response<String> {
    let mut pairs: Vec<(&str, &str)> = vec![];

    for pair in
    extract_unique_capture(text, r"[^/]+?data *?: *?\{([^{]+?)}")?.split(",")
    {
        let mut split = pair.split(":")
            .map(|str| str.trim())
            .collect::<Vec<&str>>();

        if split[1].starts_with("'") {
            split[1] = split[1].trim_matches('\'')
        } else if split[1].parse::<i32>().is_err() {
            split[1] = extract_unique_capture(text, format!(r"[^/].*?var {} ??= ??'([^']*?)'", split[1]).as_str())?;
        }

        pairs.push((split[0].trim_matches('\''), split[1]))
    };

    Ok(Serializer::new(String::new())
        .extend_pairs(pairs)
        .finish())
}

async fn get_fake_url(params: String, client: reqwest::Client) -> Response<String> {
    let resp = client.post(format!("{}/ajaxm.php", ORIGIN))
        .header(CONTENT_TYPE, HeaderValue::from_static("application/x-www-form-urlencoded"))
        .body(params)
        .send()
        .await?
        .json::<FakeResponse>()
        .await?;

    Ok(format!("{}/file/{}", resp.dom, resp.url))
}

async fn parse_fake_url_from_pc_page(file: &FileMeta) -> Response<String> {
    let client = reqwest::Client::builder()
        .default_headers(gen_default_headers!(ClientType::PC))
        .build()?;

    let text = get_text!(client, format!("{}/{}", ORIGIN, file.id));
    let params = if !file.pwd.is_empty() {
        format!("{}{}", extract_unique_capture(text.as_str(), r"[^/]+?data *?: *?'([^']+?)'")?, file.pwd)
    } else {
        let url = format!("{}{}", ORIGIN, extract_unique_capture(text.as_str(), r#"iframe.+?src="([^"]{20,}?)""#)?);
        let text = get_text!(client, url);
        parse_params(text.as_str())?
    };

    get_fake_url(params, client).await
}

async fn parse_fake_url_from_mobile_page(file: &mut FileMeta) -> Response<String> {
    let client = reqwest::Client::builder()
        .default_headers(gen_default_headers!(ClientType::MOBILE))
        .build()?;

    if !file.id.starts_with("i") {
        let text = get_text!(client, format!("{}/{}", ORIGIN, file.id));
        file.id = extract_unique_capture(text.as_str(), r"[^/\n;]+? *?= *?'tp/([^']+?)'")?.to_owned();
    }

    let mut text = get_text!(client, format!("{}/tp/{}", ORIGIN, file.id));
    if file.pwd.is_empty() {
        let path = extract_unique_capture(text.as_str(), r"[^/]+? *?= *?'(https?://[^']+)'")?;
        let params = extract_unique_capture(text.as_str(), r"[^/]+?[$\w\s]+? *?= *?'(\?[^']+?)'")?;
        Ok(format!("{}{}", path, params))
    } else {
        text = format!("{};var pwd='{}'", text, file.pwd);
        get_fake_url(parse_params(text.as_str())?, client).await
    }
}

async fn parse(mut file: FileMeta, client_type: &ClientType) -> Response<String> {
    let fake_url = match client_type {
        ClientType::PC => parse_fake_url_from_pc_page(&file).await?,
        ClientType::MOBILE => parse_fake_url_from_mobile_page(&mut file).await?,
    };

    reqwest::Client::builder()
        .default_headers(gen_default_headers!(client_type))
        .redirect(reqwest::redirect::Policy::custom(|a| a.stop()))
        .build()?
        .head(fake_url)
        .send()
        .await?
        .headers()
        .get(LOCATION).ok_or("no location header".into())
        .map(|h| h.to_str().unwrap().to_owned())
}

#[tokio::main]
async fn main() -> Response<()> {
    let mut args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        println!("Lack of arguments, examples:\n\t{}\n\t{}",
                 "parse https://lanzoui.com/iRujgdfrkza",
                 "parse https://lanzoui.com/i7tit9c 6svq");
        return Ok(());
    } else if args.len() < 3 {
        args.push("".to_owned());
    }
    args[1] = args[1].split("/").collect::<Vec<&str>>().pop().unwrap().to_owned();

    let file = FileMeta { id: args[1].to_owned(), pwd: args[2].to_owned() };
    for c in [ClientType::PC, ClientType::MOBILE] {
        let resp = parse(file.clone(), &c).await;
        if resp.is_ok() {
            println!("{}", resp?);
            return Ok(());
        }
    }

    Err("If the link and pwd are correct, the API may have changed.".into())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn parser_integration_test() -> Response<()> {
        let mut futures = vec![];

        [
            ("i7tit9c", "6svq"),
            ("i4wk2oh", ""),
            ("iRujgdfrkza", ""),
            ("dkbdv7", "")
        ]
            .iter()
            .map(|f| (f.0.to_owned(), f.1.to_owned()))
            .map(|(id, pwd)| FileMeta { id, pwd })
            .for_each(|f| [ClientType::MOBILE, ClientType::PC]
                .iter()
                .for_each(|c| futures.push(parse(f.clone(), c))));

        for f in futures {
            assert!(f.await?.starts_with("https://"));
        }

        Ok(())
    }
}